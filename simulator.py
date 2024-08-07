import sys, re

# Definição dos autômatos
# afd: {    nome: str
#           alfabeto: list
#           estados: list
#           estadoInicial: str
#           estadosFinais: list
#           transicoes: {   estado: {   simbolo: str/tuple } }
# afn: {    nome: str
#           alfabeto: list
#           estados: list
#           estadoInicial: str
#           estadosFinais: list
#           transicoes: {   estado: {   simbolo: list } }

def loadAFN(file):

    # Processa primeira linha do arquivo

    # Divide linha no '='
    first_line = file.readline().split('=', maxsplit=1)

    nome = first_line[0]

    # Expressão regular para separar os campos
    pattern = r'\{([^}]*)\}|\b(\w+)\b'

    # Para cada campo gera par (a, b)
    # a: string com termo entre {}
    # b: string com termo isolado
    # Ex: {q0, q1, q2} -> ('q0,q1,q2','')
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

    # Inicializa campos de transicoes
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

    # Salva informações no automato
    automato = { 'nome': nome,
                 'alfabeto': alfabeto,
                 'estados': estados,
                 'estadoInicial': inicial,
                 'estadosFinais': finais,
                 'transicoes': transicoes }

    return automato

# Recebe estado e codifica-o como string (concatenando estados se for tupla)
def converteEstado(estado):
    if isinstance(estado, tuple):
        return ''.join(converteEstados(estado))
    else:
        return estado

# Recebe lista/tupla de estados e devolve conjunto com todos estados codificados como string
def converteEstados(estados):
    n = []
    for estado in estados:
        n.append(converteEstado(estado))

    return sorted(set(n))

# Recebe lista e devolve string formatada como conjunto
def montaConjunto(itens):
    return '{' + ','.join(itens) + '}'

def storeAFD(file, afd):

    # Escreve primeira linha
    nome = afd['nome']
    alfabeto = montaConjunto(afd['alfabeto'])
    estados = montaConjunto(converteEstados(afd['estados']))
    inicial = converteEstado(afd['estadoInicial'])
    finais = montaConjunto(converteEstados(afd['estadosFinais']))
    first_line = nome + '=' + '(' + alfabeto + ',' + estados + ',' + inicial + ',' + finais + ')'
    file.write(first_line + '\n')

    # Escreve linha "Prog"
    file.write("Prog\n")

    # Escreve transições
    for estado_partida in afd['transicoes']:

        for simbolo, estado_chegada in afd['transicoes'][estado_partida].items():
            partida = '(' + converteEstado(estado_partida) + ',' + simbolo + ')'
            chegada = '{' + converteEstado(estado_chegada) + '}'
            transicao = partida + '=' + chegada + '\n'

            file.write(transicao)

    return file

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

    afd['transicoes'].clear() 
    for estado in tabela:
        afd['transicoes'][estado] = {}
        for simbolo in tabela[estado]:
            destino = tabela[estado][simbolo]
            if not destino:
                continue
            if len(destino) == 1:
                afd['transicoes'][estado][simbolo] = destino[0]
                continue
            afd['transicoes'][estado][simbolo] = tuple(sorted(destino))

        if not isinstance(estado, tuple) or estado in afd['estados']:
           continue

        afd['estados'].append(estado)
        for sub_estado in estado:
            if sub_estado in afd['estadosFinais']:
                afd['estadosFinais'].append(estado)
                break 

    return afd

def runAFD(automato, palavra):
    #retornar True se a palavra for aceita e False caso contrário
    estado_atual = automato['estadoInicial']

    for letra in palavra:
        if letra in automato['transicoes'][estado_atual]:
            estado_atual = automato['transicoes'][estado_atual][letra]
        else:
            return False

    if estado_atual in automato['estadosFinais']:
        return True
    else:
        return False


def runAFDPalavras(file, afd):
    palavras = file.readline().split(',')

    for palavra in palavras:
        if runAFD(afd, palavra):
            print(palavra + ': Aceita')
        else:
            print(palavra + ': Rejeita')

if __name__ == "__main__":

    # Imprime mensagem de ajuda
    if len(sys.argv) < 4 or sys.argv[1][0] == '-':
        print("Use:", sys.argv[0], "AFN AFD lista_de_palavras")
        sys.exit()

    # Abre arquivo do AFN
    try:
        with open(sys.argv[1]) as file:
            # Carrega autômato a partir do arquivo
            afn = loadAFN(file)

    except FileNotFoundError:
        print("Arquivo do AFN não encontrado")
        sys.exit()
        
    afd = AFNtoAFD(afn)

    # Abre arquivo do AFD
    with open(sys.argv[2], 'w') as file:

        # Salva autômato no arquivo
        storeAFD(file, afd)

    try:
        with open(sys.argv[3]) as file:
            runAFDPalavras(file, afd)

    except FileNotFoundError:
        print("Arquivo da lista de palavras não encontrado")
        sys.exit()
