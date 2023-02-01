del TransactionFiles\*.json.md5
del TransactionFiles\subfolder\*.json.md5
del worker_log_*.log
del commander_log.log
del server.log
cmd.exe /c "py.exe ./server.py"