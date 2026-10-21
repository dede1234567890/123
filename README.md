# Avaliação de Python — 8º ano

Prova digital da JBS FoodTech, com 20 questões.

Link para os alunos: https://diogobarao26.github.io/avaliacao-python-8ano/

Área do professor: https://diogobarao26.github.io/avaliacao-python-8ano/admin.html

Login do professor: `diogo`  
Senha: `diogo123`

Nesse link a prova abre em qualquer internet, no celular ou no computador. O professor consulta as notas pelo mesmo tipo de link, também de qualquer rede. Uma prova recém-concluída pode levar alguns minutos para aparecer. A planilha Excel e o e-mail só são gravados quando a prova roda no computador da escola, pelo `iniciar.bat`.

O repositório é público. O gabarito e também este login podem ser lidos por quem abrir o código. As notas ficam numa lista pública do próprio repositório: servem para a aula, e alguém que saiba o endereço pode consultar esses registros.

## O que a prova faz

- Pede nome completo e turma (8A, 8B, 8C, 8D ou 8E) antes de começar.
- Registra o horário de início e não deixa alterar nome ou turma.
- Mostra as instruções e, em seguida, uma questão por vez.
- Corrige no servidor, bloqueia a resposta confirmada e não permite voltar.
- As questões 1 a 8 valem 0,20 cada. As questões 9 a 20 valem 0,45 cada. A nota vai de 0 a 7,00.
- Grava a tentativa em um banco local e atualiza a planilha da turma.
- Envia um e-mail ao professor quando o servidor de e-mail está configurado.
- Se a planilha ou o e-mail falhar, a nota permanece salva e a sincronização pode ser repetida sem duplicar o aluno.

## Como iniciar na escola

1. Instale o Python 3.11 ou mais recente em um computador que os alunos alcancem pela rede.
2. Copie `backend/.env.example` para `backend/.env`.
3. O login da área do professor é `diogo` e a senha inicial é `diogo123`. No computador da escola, `ADMIN_PASSWORD` em `backend/.env` pode trocar essa senha.
4. Dê um duplo clique em `iniciar.bat`, ou execute na pasta do projeto:

```bat
py -3 -m pip install -r backend\requirements.txt
py -3 backend\app.py
```

5. O terminal mostra dois endereços. O professor usa o deste computador. Os alunos usam o endereço da rede da escola.
6. A prova fica em `http://127.0.0.1:8000`. A área do professor fica em `http://127.0.0.1:8000/admin`.

Enquanto o programa estiver aberto, a prova continua disponível. Para encerrar, feche a janela do terminal.

As planilhas ficam na pasta `data`:

- `data/notas_8A.xlsx`
- `data/notas_8B.xlsx`
- `data/notas_8C.xlsx`
- `data/notas_8D.xlsx`
- `data/notas_8E.xlsx`

O registro principal é o arquivo `data/avaliacao.sqlite3`. As planilhas são geradas de novo a partir dele, então editar uma planilha à mão não é necessário: a próxima sincronização reescreve o arquivo com todas as provas já salvas.

## Como configurar o e-mail

O destino já está definido como `diogo.nascimento@institutojef.org.br`.

No arquivo `backend/.env`, preencha os dados fornecidos pelo provedor de e-mail do instituto:

```text
SMTP_HOST=servidor informado pelo provedor
SMTP_PORT=587
SMTP_USER=usuario
SMTP_PASSWORD=senha ou senha de aplicativo
SMTP_FROM=endereco que envia a mensagem
SMTP_TO=diogo.nascimento@institutojef.org.br
SMTP_TLS=true
```

Reinicie o programa depois de salvar o arquivo. A senha não entra no JavaScript da prova.

Se esses campos estiverem vazios, o aluno ainda recebe a confirmação de que a nota foi salva. O e-mail fica pendente. Quando a configuração estiver pronta, o professor entra em `/admin` e clica em **Sincronizar planilhas e e-mails**. Cada aluno é avisado uma única vez.

## Como consultar e exportar os resultados

1. Abra `/admin` no computador que está executando a prova.
2. Entre com o login `diogo` e a senha.
3. Filtre por turma, se quiser.
4. Use os botões **Baixar notas_8A.xlsx** até **Baixar notas_8E.xlsx**.
5. Use **Sincronizar planilhas e e-mails** se alguma planilha ou mensagem tiver ficado pendente.

A coluna **Recarregamentos** conta quantas vezes a mesma sessão tentou reabrir a prova. Ela não aparece para o aluno e não muda a nota.

## Como testar as dez questões

Com as dependências instaladas, na pasta do projeto:

```bat
py -3 -m pytest backend/tests -q
```

Os testes conferem:

- nome, sobrenome e as cinco turmas;
- o gabarito das questões fechadas, inclusive executando os códigos oficiais das questões 2, 3, 5, 6, 7 e 8;
- as soluções equivalentes das questões 9 a 20, sem usar `exec` no código do aluno;
- a rejeição de código com `import`, arquivo ou laço sem fim;
- a nota 7,00 e a nota 0,00;
- a impossibilidade de responder de novo, pular questão ou trocar o nome depois do início;
- uma linha por aluno em cada planilha, mesmo com duas conclusões ao mesmo tempo;
- a repetição do e-mail sem criar outra nota;
- o acesso da área administrativa e o bloqueio de quem não entrou com a senha.

Na prova, as questões 9 a 20 pedem um programa curto: algumas para corrigir um código e outras para escrevê-lo. O servidor interpreta só os comandos previstos no enunciado (`if`, `else`, `and`, `or`, `for`, `while`, função e `print`). Ele não executa o código do aluno com o Python do computador, não abre arquivos e não acessa a rede.

## Link dos alunos no GitHub

Os alunos abrem a prova pelo GitHub Pages. Nesse link a correção acontece no próprio navegador: a nota aparece na hora, mas a planilha da turma e o e-mail ao professor não são gravados. A tela final deixa isso explícito.

O gabarito das dez questões está no arquivo `js/pages-exam.js`, e também em `backend/questions_bank.py`. Como o repositório precisa ser público para o GitHub Pages gratuito funcionar sem convite, um aluno que abrir o código consegue ver as respostas. O link serve para aplicar e treinar; ele não impede consulta ao código.

Para registrar nome, turma, nota, planilha e e-mail, use o computador da escola com `iniciar.bat`. Nesse modo o gabarito fica só no servidor e os alunos da rede não precisam do GitHub.

## Como publicar a interface

O arquivo `js/config.js` usa o modo `auto`: no endereço `github.io` a prova roda no navegador; em `localhost` ou na rede da escola ela usa o servidor.

## Cuidados

- A prova dificulta copiar e colar durante as questões. Isso não impede consulta externa, foto da tela ou as ferramentas do navegador.
- Não compartilhe a pasta `data` nem o arquivo `.env` com os alunos.
- Não guarde senha de aluno, documento ou outro dado além do nome, da turma, dos horários e da nota.
- Dois alunos podem terminar juntos: cada tentativa tem um identificador próprio e a planilha é reescrita com todas as linhas salvas.
