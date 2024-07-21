def loadAutomato(file):
    # ToDo carregar o autmato a partir de um arquivo txt

    # Definição dos autômatos
    # afd: {    alfabeto: list
    #           estados: list
    #           estadoInicial: str
    #           estadosFinais: list
    #           transicoes: {   estado: {   simbolo: str/tuple } }
    # afn: {    alfabeto: list
    #           estados: list
    #           estadoInicial: str
    #           estadosFinais: list
    #           transicoes: {   estado: {   simbolo: list } } 

    return

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

if __name__ == "__main__":

    #listas com o alfabeto em maiusculo e minusculo
    alfabeto_az = [chr(i) for i in range(ord('a'), ord('z')+1)]
    alfabeto_AZ = [chr(i) for i in range(ord('A'), ord('Z')+1)]

    #definição do automato já no codigo (o que eu mandei foro do caderno amarelo no grupo)
    automato = { 'alfabeto': alfabeto_az + alfabeto_AZ,
                 'estados': ['q0','q1','q2'],
                 'estadoInicial': 'q0',
                 'estadosFinais': ['q2'],
                 'transicoes': {'q0': {letter: 'q1' for letter in alfabeto_AZ},
                                'q1': {letter: 'q2' for letter in alfabeto_AZ},
                                'q2': {letter: 'q2' for letter in alfabeto_AZ}}}
    
    print(runAFD(automato, "gpt"))
