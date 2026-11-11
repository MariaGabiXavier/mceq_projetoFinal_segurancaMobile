# MCEQ – Projeto Final: práticas de segurança em aplicativos móveis

Projeto Final da disciplina **12576 – Métodos de Computação Experimental e Quantitativa** (Engenharia de Software, PUC-Campinas, 2026).

**Equipe:** Anna Clara Olbi, Larissa Furlan Ferreira e Maria Gabriella Xavier Puccinelli.

## Pergunta de pesquisa

Entre desenvolvedores de aplicativos móveis participantes de um survey, há diferença no número de recursos de segurança implementados entre quem afirma que os materiais de aprendizagem continham o necessário para construir aplicativos seguros (Q21 = "Sim") e quem afirma que não (Q21 = "Não")?

- **H0:** μSim = μNão
- **H1 (unilateral):** μSim > μNão
- **VI:** Q21 (percepção de suficiência dos materiais de aprendizagem)
- **VD:** Q11, contagem de 0 a 8 dos recursos de segurança que o respondente relata implementar com frequência (a opção "Other" não entra na contagem)
- **Desenho:** dois grupos independentes; estudo observacional, sem aleatorização
- **Teste principal:** t de Welch unilateral, α = 0,05. **Alternativo:** Mann–Whitney. **Efeito:** d de Cohen com IC de 95% por bootstrap

O grupo "Talvez" (n = 39) fica fora do teste confirmatório e é analisado só de forma exploratória.

## Base de dados

Peruma, A.; Huo, T.; Araújo, A. C.; Imanaka, J.; Kazman, R. *A Developer-Centric Study Exploring Mobile Application Security Practices and Challenges.* Dataset. Zenodo, versão v8, 08/09/2024.

- DOI: [10.5281/zenodo.13731929](https://doi.org/10.5281/zenodo.13731929)
- Registro: https://zenodo.org/records/13731929
- Artigo associado: https://arxiv.org/abs/2408.09032
- Data de acesso pela equipe: 03/11/2026
- Licença: CC BY 4.0, conferida no `LICENSE.txt` do pacote `Artifacts.zip`. O uso e a redistribuição exigem atribuição aos autores originais.
- Arquivo bruto usado: `SurveyResponse.csv` (137 linhas × 32 colunas), sem nenhuma edição manual.
- MD5 do registro, conferido: `4f5c6548f549f29fc59d3bc12d8bd31e`
- SHA-256 do `Artifacts.zip`: `9da7df2bb6400ff94fa5655e990665d69baa7fc5e4bf279743b93d5cfd6ded64`

## Estrutura do repositório

```
analise.py             script de análise (Q21 x Q11)
requirements.txt       bibliotecas necessárias
dados/brutos/          SurveyResponse.csv, exatamente como baixado do Zenodo
resultados/            resultados.json e figura_q21_q11 (.png e .pdf), gerados pelo script
docs/                  documentos dos Marcos 1, 2 e 3
```

## Como executar

Você precisa do **Python 3** instalado.

1. Baixe ou clone o repositório e abra um terminal dentro da pasta dele.
2. Instale as bibliotecas:

   ```
   pip install -r requirements.txt
   ```

3. Crie a pasta de saída (se ela ainda não existir):

   ```
   mkdir resultados
   ```

4. Rode o script, informando o caminho do CSV e a pasta de saída:

   ```
   python analise.py dados/brutos/SurveyResponse.csv resultados
   ```

   No Windows, se `python` não funcionar, use `py` no lugar.

O script confere por `assert` que o CSV tem 137 linhas × 32 colunas e que `Response ID` não se repete. Depois imprime a tabela descritiva por grupo e as estatísticas do teste, e salva em `resultados/` o arquivo `resultados.json` e a Figura 1.

## Resultados esperados (conferência)

| Item | Valor |
|---|---|
| n por grupo (Q21) | Sim = 17, Não = 81, Talvez = 39 |
| Médias (DP) | Sim 4,82 (1,88); Não 4,84 (1,86); Talvez 4,08 (2,01) |
| Welch unilateral | t(23,1) = −0,03; p = 0,513 |
| Mann–Whitney unilateral | U = 713,5; p = 0,408 |
| d de Cohen | −0,01 (IC 95% bootstrap: −0,54 a 0,52) |
| Kruskal–Wallis (exploratório) | H(2) = 4,06; p = 0,131 |

Decisão: não se rejeita H0. A semente do bootstrap é fixa (2026), então os números se repetem a cada execução.

## Limitações

Dados observacionais e autorrelatados; amostra intencional recrutada pelo LinkedIn; grupo "Sim" pequeno, o que reduz o poder do teste; a Q21 mede percepção, não treinamento formal em segurança. Os resultados descrevem associações e não permitem afirmações causais.
