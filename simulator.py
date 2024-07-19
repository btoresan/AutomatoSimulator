def loadAutomato(file):
    #ToDo carregar o autmato a partir de um arquivo txt
    #definição do automato {alfabeto = list(chars)
    #                        estados = list(str)
    #                        estadoInicial = str
    #                        estadosFinais = list(str)
    #                        transicoes = dict{estado:dict{char:list(estado)}} <- list(estados) caso seja AFN

    return

def AFNtoAFD(afn):
    #ToDo
    return

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