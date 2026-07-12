"""
Armazenamento em memória do progresso e resultado das conversões.

progress_queues: dict[job_id] -> queue.Queue
finished_jobs:   dict[job_id] -> caminho do arquivo .xlsx gerado

Por ser em memória, esse estado é perdido quando o processo é reiniciado e
não é compartilhado entre múltiplos processos/workers. Para uma aplicação
de uso pessoal/local rodando com um único processo (como esta), isso é
suficiente.
"""

progress_queues = {}
finished_jobs = {}
