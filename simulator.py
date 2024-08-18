import sys, re

# Definições:
#
# estado: str
#
# simbolo: str
#
# afd: {    nome: str
#           alfabeto: list
#           estados: list
#           estadoInicial: str
#           estadosFinais: list
#           transicoes: {   estado: {   simbolo: list } }
#
# afn: {    nome: str
#           alfabeto: list
#           estados: list
#           estadoInicial: str
#           estadosFinais: list
#           transicoes: {   estado: {   simbolo: list } }

# Recebe arquivo com um AFN
# Retorna AFN lido do arquivo
def loadAFN(file):

    # Processa primeira linha do arquivo

    # Divide linha no '='
    first_line = file.readline().split('=', maxsplit=1)

    nome = first_line[0]

    # Expressão regular para separar os campos
    pattern = r'\{([^}]*)\}|\b(\w+)\b'

    # Para cada campo gera par (a, b)
    # a: string entre chaves
    # b: string não entre chaves
    # Ex: {q0,q1,q2} -> ('q0,q1,q2','')
    # Ex: q0 -> ('', 'q0')
    campos = re.findall(pattern, first_line[1])

    # Processa os campos
    for i, campo in enumerate(campos):
        items = campo[0].split(',')

        match i:
            case 0:
                alfabeto = items

            case 1:
                estados = items

            case 2:
                inicial = campo[1]

            case 3:
                finais = items

    # Lê linha "Prog"
    file.readline()

    # Inicializa campos de transições
    transicoes = {}
    for estado in estados:
        transicoes[estado] = {}

    # Processa demais linhas (transições)
    for line in file:
        # Divide linha no '='
        prog_line = line.rsplit('=', maxsplit=1)

        # Remove delimitadores
        partida = prog_line[0][1:-1].split(',', maxsplit=1)
        estado_chegada = prog_line[1][1:-2].split(',')

        estado_partida = partida[0]
        simbolo = partida[1]

        # Monta transição
        transicoes[estado_partida][simbolo] = estado_chegada

    # Monta autômato
    afn = { 'nome': nome,
            'alfabeto': alfabeto,
            'estados': estados,
            'estadoInicial': inicial,
            'estadosFinais': finais,
            'transicoes': transicoes }

    return afn

# Recebe lista de strings
# Retorna string formatada como conjunto
def montaConjunto(itens):
    return '{' + ','.join(itens) + '}'

# Recebe um arquivo e um AFD
# Escreve AFD no arquivo
def storeAFD(file, afd):

    # Escreve primeira linha
    nome = afd['nome']
    alfabeto = montaConjunto(afd['alfabeto'])
    estados = montaConjunto(afd['estados'])
    inicial = afd['estadoInicial']
    finais = montaConjunto(afd['estadosFinais'])
    first_line = nome + '=' + '(' + alfabeto + ',' + estados + ',' + inicial + ',' + finais + ')'
    file.write(first_line + '\n')

    # Escreve linha "Prog"
    file.write("Prog\n")

    # Escreve transições
    for estado_partida in afd['transicoes']:

        for simbolo, estado_chegada in afd['transicoes'][estado_partida].items():
            partida = '(' + estado_partida + ',' + simbolo + ')'
            chegada = '{' + estado_chegada + '}'
            transicao = partida + '=' + chegada + '\n'

            file.write(transicao)

# Recebe um estado ou uma tupla de estados
# Retorna estado codificado como string (concatenando estados se for tupla)
def converteEstado(estado):
    if isinstance(estado, tuple):
        return ''.join(converteEstados(estado))
    else:
        return estado

# Recebe lista de estados ou tuplas de estados
# Retorna lista com todos estados codificados como string
def converteEstados(estados):
    n = []
    for estado in estados:
        n.append(converteEstado(estado))

    return sorted(set(n))

# Recebe um AFN
# Retorna AFD equivalente
def AFNtoAFD(afn):

    afd = afn.copy()

    # Cria tabela para adicionar estados determinizados 
    tabela = {}
    for estado in afn['estados']:
        tabela[estado] = {}
        for simbolo in afn['alfabeto']:
            valor = []
            try:
                valor = afn['transicoes'][estado][simbolo].copy()
            except Exception:
                pass
            tabela[estado][simbolo] = valor

    # Passa pela tabela adicionando novos estados 
    estados_adicionados = []
    mudanca = True
    while mudanca:
        mudanca = False

        # Adiciona os novos estados determinizados à tabela
        for novo_estado in estados_adicionados:
            tabela[novo_estado] = {}
            for simbolo in afn['alfabeto']:
                valor = []
                for estado in novo_estado:
                    try:
                        valor += afn['transicoes'][estado][simbolo] 
                    except KeyError:
                        pass
                tabela[novo_estado][simbolo] = valor

        # Passa procurando novos estados para determinizar 
        estados_adicionados.clear()
        for estado in tabela:
            for simbolo in tabela[estado]:
                destinos = tabela[estado][simbolo]
                if not destinos or len(destinos) == 1:
                    continue
                novo_estado = tuple(sorted(destinos))
                if novo_estado in estados_adicionados or novo_estado in tabela:
                    continue
                estados_adicionados.append(novo_estado)
                mudanca = True

    # Monta autômato
    afd['transicoes'].clear() 
    for estado in tabela:
        afd['transicoes'][converteEstado(estado)] = {}
        for simbolo in tabela[estado]:
            destino = tabela[estado][simbolo]
            if not destino:
                continue
            if len(destino) == 1:
                afd['transicoes'][converteEstado(estado)][simbolo] = converteEstado(destino[0])
                continue
            afd['transicoes'][converteEstado(estado)][simbolo] = converteEstado(tuple(sorted(destino)))

        if not isinstance(estado, tuple) or estado in afd['estados']:
           continue

        afd['estados'].append(converteEstado(estado))
        for sub_estado in estado:
            if sub_estado in afd['estadosFinais']:
                afd['estadosFinais'].append(converteEstado(estado))
                break

    return afd

# Recebe um AFD e uma palavra
# Retorna True se a palavra for aceita pelo AFD e False caso contrário
def runAFD(afd, palavra):
   
    estado_atual = afd['estadoInicial']

    for letra in palavra:
        if letra in afd['transicoes'][estado_atual]:
            estado_atual = afd['transicoes'][estado_atual][letra]
        else:
            return False

    if estado_atual in afd['estadosFinais']:
        return True
    else:
        return False

# Recebe arquivo com uma lista de palavras e um AFD
# Imprime na tela as palavras aceitas
def runAFDfile(file, afd):
    palavras = file.readline().split(',')

    print("Palavras aceitas:")

    for palavra in palavras:
        if runAFD(afd, palavra):
            print(palavra)

if __name__ == "__main__":

    # Imprime mensagem de ajuda
    if len(sys.argv) < 4:
        print("Indique os arquivos necessários:")
        print(sys.argv[0], "AFN AFD lista_de_palavras")
        sys.exit()

    # Carrega AFN a partir do arquivo
    try:
        with open(sys.argv[1]) as file:
            afn = loadAFN(file)

    except FileNotFoundError:
        print("Arquivo do AFN não encontrado")
        sys.exit()
        
    # Converte AFN para AFD
    afd = AFNtoAFD(afn)

    # Salva AFD no arquivo
    with open(sys.argv[2], 'w') as file:
        storeAFD(file, afd)

    # Imprime palavras da lista aceitas pelo AFD
    try:
        with open(sys.argv[3]) as file:
            runAFDfile(file, afd)

    except FileNotFoundError:
        print("Arquivo da lista de palavras não encontrado")
        sys.exit()
