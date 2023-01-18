# CK3-gcloud-translation
Script e arquivos de tradução do CK3

Para poder executar o script é preciso ter uma conta da google cloud com o serviço da Cloud Translation API ativado.
Siga o link para saber como configurar seu ambiente:
https://cloud.google.com/translate/docs/setup

Lembre de trocar o project_id na função `translate_text()`

Depois de configurado, para traduzir algum arquivo de tradução do CK3 basta rodar o comando:
`python replace_script.py CAMINHO_DO_ARQUIVO`

Na pasta 'traducao_ptbr_cloud' estão localizados os arquivos do mod.
