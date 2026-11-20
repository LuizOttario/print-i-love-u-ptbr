# Print I Love U — Tradução PT-BR (português do Brasil)

Tradução não oficial, feita por fã, do jogo **Print I Love U** (Steam) para **português do Brasil**.

O jogo não tem opção de português. Por isso, esta tradução **substitui os textos em inglês**:
deixe o jogo em **English** e ele vai aparecer em PT-BR.

Este repositório **não contém arquivos do jogo**. O script lê o `languages.json` da sua própria
cópia do jogo e troca só os textos em inglês. Os outros idiomas ficam intactos.

## Como instalar

Você precisa ter o Python 3 instalado.

1. Baixe este repositório (botão **Code → Download ZIP**) e extraia.
2. Ache a pasta do jogo: na Steam, clique com o botão direito no jogo → **Gerenciar → Procurar arquivos locais**.
3. Faça um backup do `languages.json` original com o nome `languages.json.bak`.
4. Rode, de dentro da pasta deste repositório:

```bash
python3 apply.py "CAMINHO/DO/JOGO/languages.json.bak" "CAMINHO/DO/JOGO/languages.json"
```

Exemplos de caminho:
- Linux: `~/.local/share/Steam/steamapps/common/Print I Love U`
- Windows: `C:\Program Files (x86)\Steam\steamapps\common\Print I Love U` (use `python` em vez de `python3`)

Se aparecer `OK`, está pronto. O script confere se todas as 224 chaves estão no lugar e se a
formatação do arquivo foi preservada.

### Acentos aparecendo como quadrado?

As fontes do jogo não têm `ã` nem `õ`. Se aparecerem quadrados, rode o mesmo comando com
`alt` no final. Essa versão troca `ã`→`a` e `õ`→`o`:

```bash
python3 apply.py "CAMINHO/DO/JOGO/languages.json.bak" "CAMINHO/DO/JOGO/languages.json" alt
```

### Desinstalar

Copie o `languages.json.bak` de volta para `languages.json`, ou use a opção da Steam
**Propriedades → Arquivos instalados → Verificar integridade**. A Steam também pode voltar o
arquivo original quando o jogo atualizar. Se isso acontecer, é só rodar o script de novo.

## Arquivos

- `pt.py` — todos os textos traduzidos
- `apply.py` — aplica a tradução no `languages.json` do jogo e valida o resultado

Print I Love U pertence aos seus criadores. Este é um projeto de fã, sem fins lucrativos.
