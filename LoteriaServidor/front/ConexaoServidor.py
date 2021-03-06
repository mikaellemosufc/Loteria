#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import thread
import pickle
import random

from Banco import *
from Email import *


HOST = ''              # Endereco IP do Servidor
PORT = 12345           # Porta que o Servidor está


class Person(object):
    def __init__(self, id_pessoa, nome, idade, cpf, endereco, login, senha, email, cartao, conta, acao):
        self.id_pessoa = id_pessoa
        self.nome = nome
        self.idade = idade
        self.cpf = cpf
        self.endereco = endereco
        self.login = login
        self.senha = senha
        self.email = email
        self.cartao = cartao
        self.conta = conta
        self.acao = acao



class Aposta(object):
    def __init__(self, id_aposta, campo1, campo2, campo3, campo4, campo5, campo6, id_pessoa, acao):
        self.id_aposta = id_aposta
        self.campo1 = campo1
        self.campo2 = campo2
        self.campo3 = campo3
        self.campo4 = campo4
        self.campo5 = campo5
        self.campo6 = campo6
        self.id_pessoa = id_pessoa
        self.acao = acao



def conectado(con, cliente):
    print 'Conectado por', cliente

    while True:
        serializado = con.recv(1024)
        try:
            msg = pickle.loads(serializado)
        except EOFError:
            desconectar(con, cliente)
        #if not msg: break
        if msg.acao == 'CADASTRAR':
            nome1 = msg.nome
            idade1 = int(msg.idade)
            cpf1 = msg.cpf
            endereco1 = msg.endereco
            login1 = msg.login
            senha1 = msg.senha
            email1 = str(msg.email)
            cartao1 = msg.cartao
            conta1 = msg.conta

            banco = DAO()

            args = (nome1, idade1, cpf1, endereco1, login1, senha1, email1, cartao1, conta1)
            bole = banco.inserir("INSERT INTO pessoa (nome, idade, cpf, endereco, login, senha, email, cartao, conta) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", args)
            if bole == True:
                serumano = Person(None, None, None, None, None, None, None, None, None, None, 'CADASTRADO')
                serializadoResposta = pickle.dumps(serumano)
                enviar(con, cliente, serializadoResposta)
                print ("CADASTRADO")
            else:
                serumano = Person(None, None, None, None, None, None, None, None, None, None, 'NÃO CADASTRADO')
                serializadoResposta = pickle.dumps(serumano)
                enviar(con, cliente, serializadoResposta)
                print ("NÃO CADASTRADO")


        if msg.acao == 'LOGAR':
            banco = DAO()

            login1 = msg.login
            senha1 = msg.senha
            boli = banco.lerLogin("SELECT id_pessoa, login, senha, nome, cpf, endereco, email, cartao, conta FROM pessoa", login1, senha1)
            
            if boli.nome != None:
                serumano = Person(boli.id_pessoa, boli.nome, None, boli.cpf, boli.endereco, boli.login, boli.senha, boli.email, boli.cartao, boli.conta, 'LOGADO')
                serializadoResposta = pickle.dumps(serumano)
                enviar(con, cliente, serializadoResposta)
                print ("LOGADO")
            else:
                serumano = Person(None, None, None, None, None, None, None, None, None, None, 'NÃO LOGOU')
                serializadoResposta = pickle.dumps(serumano)
                enviar(con, cliente, serializadoResposta)
                print ("NÃO LOGOU")


        if msg.acao == 'APOSTAR':
            campo1 = msg.campo1
            campo2 = msg.campo2
            campo3 = msg.campo3
            campo4 = msg.campo4
            campo5 = msg.campo5
            campo6 = msg.campo6
            id_pessoa1 = msg.id_pessoa

            banco = DAO()

            args = (campo1, campo2, campo3, campo4, campo5, campo6, id_pessoa1)
            bole = banco.inserirAposta("INSERT INTO aposta (campo1, campo2, campo3, campo4, campo5, campo6, id_pessoa) VALUES (%s, %s, %s, %s, %s, %s, %s)", args)
            if bole == True:
                apostinha = Aposta(None, None, None, None, None, None, None, None, 'APOSTADO')
                serializadoResposta = pickle.dumps(apostinha)
                enviar(con, cliente, serializadoResposta)
                print ("APOSTADO")
            else:
                apostinha = Aposta(None, None, None, None, None, None, None, None, 'NÃO APOSTADO')
                serializadoResposta = pickle.dumps(apostinha)
                enviar(con, cliente, serializadoResposta)
                print ("NÃO APOSTADO")



def enviar(con, cliente, sMessage):    
    #while True:
    #sMessage = raw_input(">>")
    #if not sMessage: break
    con.send(sMessage)



def desconectar(con, cliente):
    print 'Finalizando conexão do cliente', cliente
    con.close()
    thread.exit()



def realizarSorteio():
    lista = sorted(random.sample(range(0,99), 6))
    
    campo1 = lista[0]
    campo2 = lista[1]
    campo3 = lista[2]
    campo4 = lista[3]
    campo5 = lista[4]
    campo6 = lista[5]
    
    banco = DAO()

    #CAMPOS PARA AMOSTRA DE VENCEDOR
    """
    campo1 = 12
    campo2 = 12
    campo3 = 12
    campo4 = 12
    campo5 = 12
    campo6 = 12
    """
    valor = 100000

    ganhaste = banco.lerSorteio("SELECT id_aposta, campo1, campo2, campo3, campo4, campo5, campo6, id_pessoa FROM aposta", campo1, campo2, campo3, campo4, campo5, campo6)

    if len(ganhaste) > 0:
        valor = valor/len(ganhaste)
        valor = str(valor)
        print 'HOUVE ' + str(len(ganhaste)) +' GANHADOR(ES)'
        i = 0
        while i < len(ganhaste):
            auxiliavendedor = banco.buscarPessoa(ganhaste[i].id_pessoa)
            vencedor = Email(auxiliavendedor.email, 'Parabéns, você ganhou na loteria', 'Parabéns, você foi o grande ganhador da loteria neste mês! Entre em contato conosco pelo número 4002-8922 para que possa receber teu prêmio de ' + valor +'. Não se esqueça de estar com seus documentos em mãos.')
            vencedor.enviar()
            i = i+1

            banco.apagar('DELETE FROM aposta WHERE id_aposta >= 0')
    else:
        print 'NÃO HOUVE GANHADOR'



#CRIANDO A CONEXÃO TCP DO SERVIDOR
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

orig = (HOST, PORT)
tcp.bind(orig)
tcp.listen(1)



#MENU DO SERVIDOR
print (30 * '-')
print ("   SERVIDOR - M E N U")
print (30 * '-')
print ("1. Iniciar o Servidor")
print ("2. Realizar um Sorteio")
print (30 * '-')

opc = raw_input('Digite sua escolha [1-2]: ')

if opc == '1':
    while True:
        con, cliente = tcp.accept()
        thread.start_new_thread(conectado, tuple([con, cliente]))
        #thread.start_new_thread(enviar, tuple([con, cliente]))
else:
    realizarSorteio()

tcp.close()
