# Leitor de imagem FAT16 - Guilherme Deitos e Vinicius Viana
import sys
 
# Classe FAT16
class FAT16():
    # Definir atributos
    numFATs = 0 # Numero de tabelas FAT
    totalSectors = 0 # Numero total de setores
    sectorsPerFAT = 0 # Numero de setores por FAT
    sectorsPerCluster = 0 # Numero de setores por cluster
    bytesPerSector = 0
    arquivos83 = [] # lista de Arquivos no formatro 8.3
    posReservedSectors = 0 # Posição do setor reservado
    posRootDir = 0 # Posição do diretório raiz
    posDataRegion = 0 # Posição da região de dados
    posFATS = [] # Posição das FATs
    FATsize = 0 # Tamanho da FAT
    numRootDirEntries = 0 # Entradas do diretório raiz
    image = 0 # Imagem
    
    
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = self.open_image(image_path)
        self.boot_record = self.read_boot_record()
        self.fat = self.read_fat()
        self.root_dir = self.read_root_dir()
        self.data_region = self.read_data_region()
        self.arquivos83 = self.list_files()
        self.show_image_info = self.read_show_image_info()        

    # Função pra abrir a imagem
    def open_image(self,image_path):
        try:
            # Abre a imagem passada por parametro e retorna o conteudo
            with open(image_path, "rb") as image:
                return image.read()
        except FileNotFoundError:
            print("Arquivo não encontrado")
            sys.exit(1)

    # Função pra ler o boot record
    def read_boot_record(self):
        boot_record = self.image[0:512] 
        self.bytesPerSector = int.from_bytes(boot_record[11:13], byteorder="little")
        self.sectorsPerCluster = int.from_bytes(boot_record[13:14], byteorder="little")
        self.posReservedSectors = int.from_bytes(boot_record[14:16], byteorder="little")
        self.numFATs = int.from_bytes(boot_record[16:17], byteorder="little")
        self.numRootDirEntries = int.from_bytes(boot_record[17:19], byteorder="little")
        self.totalSectors = int.from_bytes(boot_record[19:21], byteorder="little")
        self.sectorsPerFAT = int.from_bytes(boot_record[22:24], byteorder="little")
        self.FATsize = self.sectorsPerFAT * self.bytesPerSector
        self.posFATS = [self.posReservedSectors * self.bytesPerSector + (self.FATsize * i) for i in range(self.numFATs)]
        self.posRootDir = self.posFATS[0] + (self.FATsize * self.numFATs)
        self.posDataRegion = self.posRootDir + (self.numRootDirEntries * 32)    

        return boot_record

    # Função pra ler a FAT
    def read_fat(self):
        fat = self.image[self.posFATS[0]:self.posFATS[0] + (self.sectorsPerFAT * self.bytesPerSector)]
        return fat
    
    # Função pra ler o diretório raiz
    def read_root_dir(self):
        root_dir = self.image[self.posRootDir:self.posDataRegion]
        return root_dir
    
    # Função pra ler a região de dados
    def read_data_region(self):
        data_region = self.image[self.posDataRegion:]
        return data_region
    
    # Função pra armazenar apenas os arquivos 8.3
    def list_files(self):
        arquivos = []
        for i in range(0, len(self.root_dir), 32):
            # Ignora os bytes zerados, de arquivos excluidos e com atributo LFN
            if self.root_dir[i] != 0x00 and self.root_dir[i] != 0xE5 and self.root_dir[i+11] != 0x0F:
                arquivos.append(self.root_dir[i:i+32])
        return arquivos
    
    # Função pra printar o nome, primeiro cluster e tamanho dos arquivos 8.3
    def list_83_files(self):
        for arquivo in self.arquivos83:
            print("\033[32m",arquivo[0:8].decode("utf-8").rstrip(), end="")
            print(".", end="")
            print(arquivo[8:11].decode("utf-8").rstrip())
            print("Primeiro Cluster: ", int.from_bytes(arquivo[26:28], byteorder="little"))
            print("Tamanho: ", int.from_bytes(arquivo[28:32], byteorder="little"), "bytes \033[0m")
        
    # Função para mostrar as informações da imagem
    def read_show_image_info(self):
        print("--------------------------------")
        print("Informações da imagem:")
        print("Bytes por setor: ", self.bytesPerSector)
        print("Setores por cluster: ", self.sectorsPerCluster)
        print("Setores reservados: ", self.posReservedSectors)
        print("Numero de FATs: ", self.numFATs)
        print("Entradas do diretório raiz: ", self.numRootDirEntries)
        print("Total de setores: ", self.totalSectors)
        print("Setores por FAT: ", self.sectorsPerFAT)
        numFat = 1
        for i in self.posFATS:
            print(f"Posição da FAT{numFat}: {hex(i)}")
            numFat+=1
        print("Posição do diretório raiz: ", hex(self.posRootDir))
        print("Posição da região de dados: ", hex(self.posDataRegion))
        print("Arquivos no formato 8.3:")
        print("--------------------------------")
        self.list_83_files()   
        print("--------------------------------")
        return self

        
def main():
    # Execução do programa passando por parametro o nome do arquivo de imagem
    if len(sys.argv) < 2:
        print("Uso: python3 LeitorFAT16.py <nome da imagem>")
        sys.exit(1)
    image_name = sys.argv[1]
    FAT16(image_name)

if __name__ == "__main__":
    main()