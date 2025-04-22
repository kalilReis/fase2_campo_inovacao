import json
import os
from datetime import datetime
import oracledb

class GerenciadorColheita:
    def __init__(self):
        self.dados_colheita = []
        self.colhedoras = {}
        # Create base directory path
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.dados_dir = os.path.join(self.base_dir, 'dados')
        self.dados_file = os.path.join(self.dados_dir, 'colheitas.json')
        
        # Ensure dados directory exists
        os.makedirs(self.dados_dir, exist_ok=True)
        
        # Criar tabela se não existir
        self.criar_tabela()
        self.carregar_dados()

    def criar_tabela(self):
        """Cria a tabela no banco de dados se não existir"""
        try:
            conexao = oracledb.connect(
                user="system",
                password="admin",
                dsn="localhost/FREEPDB1"
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
            if 'conexao' in locals():
                conexao.close()

    def carregar_dados(self):
        """Carrega dados do arquivo JSON se existir"""
        try:
            with open(self.dados_file, 'r') as arquivo:
                self.dados_colheita = json.load(arquivo)
        except FileNotFoundError:
            self.dados_colheita = []

    def salvar_dados(self):
        """Salva dados no arquivo JSON"""
        with open(self.dados_file, 'w') as arquivo:
            json.dump(self.dados_colheita, arquivo, indent=4)

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
            "percentual_perda": (toneladas_perdidas / total_toneladas) * 100
        }
        
        self.dados_colheita.append(registro_colheita)
        self.salvar_dados()
        return registro_colheita

    def calcular_perdas(self) -> tuple:
        """Calcula média de perdas"""
        if not self.dados_colheita:
            return (0, 0)
        
        total_perdido = sum(registro["toneladas_perdidas"] for registro in self.dados_colheita)
        media_percentual_perda = sum(registro["percentual_perda"] for registro in self.dados_colheita) / len(self.dados_colheita)
        return (total_perdido, media_percentual_perda)

    def salvar_no_banco(self, registro_colheita: dict):
        """Salva dados da colheita no banco Oracle"""
        try:
            conexao = oracledb.connect(
                user="system",
                password="admin",
                dsn="localhost/FREEPDB1"
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
            print("Dados salvos no banco com sucesso!")
            
        except oracledb.Error as erro:
            print(f"Erro no banco de dados: {erro}")
        finally:
            if 'conexao' in locals():
                conexao.close()

def main():
    gerenciador = GerenciadorColheita()
    
    while True:
        print("\n=== Gerenciador de Colheita de Cana ===")
        print("1. Registrar nova colheita")
        print("2. Ver estatísticas de perdas")
        print("3. Sair")
        
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
            print("Encerrando o programa...")
            break
            
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()