import os
import json # Import json module
from datetime import datetime
import oracledb
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Obter credenciais do banco de dados das variáveis de ambiente
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")

# Verificar se as variáveis de ambiente foram carregadas
if not all([DB_USER, DB_PASSWORD, DB_DSN]):
    print("Erro: Variáveis de ambiente do banco de dados (DB_USER, DB_PASSWORD, DB_DSN) não configuradas.")
    # Considerar sair do script ou usar valores padrão/lançar exceção
    # exit(1) # Descomente para sair se as variáveis não estiverem definidas

class GerenciadorColheita:
    def __init__(self):
        self.colhedoras = {}
        # Criar tabela se não existir
        self.criar_tabela()

    def criar_tabela(self):
        """Cria a tabela no banco de dados se não existir"""
        try:
            # Usar variáveis de ambiente para a conexão
            conexao = oracledb.connect(
                user=DB_USER,
                password=DB_PASSWORD,
                dsn=DB_DSN
            )
            cursor = conexao.cursor()
            
            cursor.execute("""
                BEGIN
                    EXECUTE IMMEDIATE 'CREATE TABLE registros_colheita (
                        id NUMBER GENERATED ALWAYS AS IDENTITY,
                        data_colheita DATE,
                        area_hectares NUMBER(10,2),
                        id_colhedora VARCHAR2(50),
                        total_toneladas NUMBER(10,2),
                        toneladas_perdidas NUMBER(10,2),
                        percentual_perda NUMBER(5,2),
                        CONSTRAINT pk_registros_colheita PRIMARY KEY (id)
                    )';
                EXCEPTION
                    WHEN OTHERS THEN
                        IF SQLCODE != -955 THEN
                            RAISE;
                        END IF;
                END;
            """)
            conexao.commit()

        except oracledb.Error as erro:
            print(f"Erro ao criar tabela: {erro}")
        finally:
            if 'conexao' in locals() and conexao.is_healthy():
                conexao.close()

    def registrar_colheita(self, area_hectares: float, id_colhedora: str,
                          total_toneladas: float, toneladas_perdidas: float) -> dict:
        """Registra novos dados de colheita"""
        if toneladas_perdidas > total_toneladas:
            raise ValueError("Toneladas perdidas não pode ser maior que o total colhido")
            
        registro_colheita = {
            "data": datetime.now().strftime("%Y-%m-%d"),
            "area_hectares": area_hectares,
            "id_colhedora": id_colhedora,
            "total_toneladas": total_toneladas,
            "toneladas_perdidas": toneladas_perdidas,
            "percentual_perda": (toneladas_perdidas / total_toneladas) * 100 if total_toneladas > 0 else 0
        }
        # Não salva mais em JSON nem adiciona a lista local
        return registro_colheita

    def ler_dados_do_banco(self) -> list:
        """Lê todos os registros de colheita do banco de dados"""
        dados = []
        try:
            # Usar variáveis de ambiente para a conexão
            conexao = oracledb.connect(
                user=DB_USER,
                password=DB_PASSWORD,
                dsn=DB_DSN
            )
            cursor = conexao.cursor()
            cursor.execute("SELECT data_colheita, area_hectares, id_colhedora, total_toneladas, toneladas_perdidas, percentual_perda FROM registros_colheita ORDER BY data_colheita")
            
            # Fetch column names to create dictionaries
            colnames = [desc[0].lower() for desc in cursor.description]
            
            for row in cursor.fetchall():
                registro = dict(zip(colnames, row))
                # Convert date object back to string if needed, or handle as date object
                if isinstance(registro.get('data_colheita'), datetime):
                     registro['data_colheita'] = registro['data_colheita'].strftime("%Y-%m-%d")
                dados.append(registro)
                
        except oracledb.Error as erro:
            print(f"Erro ao ler dados do banco: {erro}")
        finally:
            if 'conexao' in locals() and conexao.is_healthy():
                conexao.close()
        return dados

    def listar_todas_colheitas(self):
        """Lista todos os registros de colheita formatados"""
        dados = self.ler_dados_do_banco()
        if not dados:
            print("\nNenhum registro de colheita encontrado.")
            return

        print("\n--- Todos os Registros de Colheita ---")
        for registro in dados:
            print(f"Data: {registro.get('data_colheita', 'N/A')}, "
                  f"Área (ha): {registro.get('area_hectares', 'N/A'):.2f}, "
                  f"Colhedora: {registro.get('id_colhedora', 'N/A')}, "
                  f"Total (ton): {registro.get('total_toneladas', 'N/A'):.2f}, "
                  f"Perdido (ton): {registro.get('toneladas_perdidas', 'N/A'):.2f}, "
                  f"Perda (%): {registro.get('percentual_perda', 'N/A'):.2f}%")
        print("--------------------------------------")


    def calcular_perdas(self) -> tuple:
        """Calcula média de perdas lendo do banco de dados"""
        dados_colheita_db = self.ler_dados_do_banco()
        if not dados_colheita_db:
            return (0, 0)

        total_perdido = sum(registro["toneladas_perdidas"] for registro in dados_colheita_db if registro.get("toneladas_perdidas") is not None)
        # Ensure percentual_perda exists and is not None before summing
        valid_percentual_perda = [registro["percentual_perda"] for registro in dados_colheita_db if registro.get("percentual_perda") is not None]
        
        if not valid_percentual_perda:
             media_percentual_perda = 0
        else:
             media_percentual_perda = sum(valid_percentual_perda) / len(valid_percentual_perda)
             
        return (total_perdido, media_percentual_perda)

    def salvar_no_banco(self, registro_colheita: dict):
        """Salva dados da colheita no banco Oracle"""
        # Basic validation before saving
        required_keys = ["data", "area_hectares", "id_colhedora", "total_toneladas", "toneladas_perdidas", "percentual_perda"]
        if not all(key in registro_colheita for key in required_keys):
            print(f"Erro: Registro inválido, faltando chaves. Registro: {registro_colheita}")
            return False # Indicate failure

        try:
            # Usar variáveis de ambiente para a conexão
            conexao = oracledb.connect(
                user=DB_USER,
                password=DB_PASSWORD,
                dsn=DB_DSN
            )
            cursor = conexao.cursor()
            
            # Convert string date to Oracle date format
            data = datetime.strptime(registro_colheita["data"], "%Y-%m-%d")
            
            sql = """INSERT INTO registros_colheita 
                     (data_colheita, area_hectares, id_colhedora, total_toneladas, 
                      toneladas_perdidas, percentual_perda)
                     VALUES (:1, :2, :3, :4, :5, :6)"""
            
            cursor.execute(sql, (
                data,  # Send datetime object instead of string
                registro_colheita["area_hectares"],
                registro_colheita["id_colhedora"],
                registro_colheita["total_toneladas"],
                registro_colheita["toneladas_perdidas"],
                registro_colheita["percentual_perda"]
            ))
            
            conexao.commit()
            # print("Dados salvos no banco com sucesso!") # Make it less verbose for bulk import
            return True # Indicate success

        except oracledb.Error as erro:
            print(f"Erro no banco de dados ao salvar {registro_colheita.get('id_colhedora', 'registro')}: {erro}")
            return False # Indicate failure
        finally:
            if 'conexao' in locals() and conexao.is_healthy():
                conexao.close()

    def importar_de_json(self, caminho_arquivo: str):
        """Importa dados de colheita de um arquivo JSON para o banco"""
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                dados_json = json.load(f)
        except FileNotFoundError:
            print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
            return
        except json.JSONDecodeError:
            print(f"Erro: Falha ao decodificar JSON do arquivo '{caminho_arquivo}'. Verifique o formato.")
            return
        except Exception as e:
            print(f"Erro ao ler o arquivo '{caminho_arquivo}': {e}")
            return

        if not isinstance(dados_json, list):
            print("Erro: O arquivo JSON deve conter uma lista de registros de colheita.")
            return

        registros_importados = 0
        registros_falha = 0
        print(f"\nIniciando importação de '{caminho_arquivo}'...")

        for registro in dados_json:
            # Basic validation (can be expanded)
            if isinstance(registro, dict):
                 # Ensure required keys exist, maybe add type checks later
                 required = ["data", "area_hectares", "id_colhedora", "total_toneladas", "toneladas_perdidas"]
                 if all(k in registro for k in required):
                     # Calculate percentual_perda if not present or overwrite
                     total = registro.get("total_toneladas", 0)
                     perdido = registro.get("toneladas_perdidas", 0)
                     registro["percentual_perda"] = (perdido / total) * 100 if total > 0 else 0

                     if self.salvar_no_banco(registro):
                         registros_importados += 1
                     else:
                         registros_falha += 1
                 else:
                    print(f"Aviso: Registro ignorado por falta de chaves obrigatórias: {registro}")
                    registros_falha += 1
            else:
                print(f"Aviso: Item ignorado no JSON (não é um dicionário): {registro}")
                registros_falha += 1

        print(f"Importação concluída: {registros_importados} registros importados com sucesso, {registros_falha} falharam ou foram ignorados.")


def main():
    gerenciador = GerenciadorColheita()
    
    while True:
        print("\n=== Gerenciador de Colheita de Cana ===")
        print("1. Registrar nova colheita")
        print("2. Ver estatísticas de perdas")
        print("3. Listar todas as colheitas")
        print("4. Importar dados de JSON") # Nova opção de importação
        print("5. Sair") # Opção Sair agora é 5

        opcao = input("Selecione uma opção: ")
        
        if opcao == "1":
            try:
                area = float(input("Área colhida (hectares): "))
                if area <= 0:
                    raise ValueError("Área deve ser maior que zero")
                    
                colhedora = input("ID da colhedora: ")
                if not colhedora.strip():
                    raise ValueError("ID da colhedora não pode ser vazio")
                    
                total = float(input("Total de toneladas colhidas: "))
                if total <= 0:
                    raise ValueError("Total deve ser maior que zero")
                    
                perdido = float(input("Toneladas estimadas perdidas: "))
                if perdido < 0:
                    raise ValueError("Perdas não podem ser negativas")
                
                registro = gerenciador.registrar_colheita(area, colhedora, total, perdido)
                gerenciador.salvar_no_banco(registro)
                print("Dados da colheita registrados com sucesso!")
                
            except ValueError as e:
                print(f"Erro: {str(e)}")
                
        elif opcao == "2":
            total_perdido, media_perda = gerenciador.calcular_perdas()
            print(f"\nTotal de toneladas perdidas: {total_perdido:.2f}")
            print(f"Percentual médio de perda: {media_perda:.2f}%")

        elif opcao == "3":
            gerenciador.listar_todas_colheitas()

        elif opcao == "4": # Nova opção para importar
            caminho_json = input("Digite o caminho para o arquivo JSON de importação: ")
            gerenciador.importar_de_json(caminho_json)

        elif opcao == "5": # Opção Sair agora é 5
            print("Encerrando o programa...")
            break
            
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
