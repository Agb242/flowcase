import time
import datetime
# Import db lazily inside functions to avoid circular imports

def log(level: str, message: str):
	"""Log a message to the database and console"""
	from models.log import Log
	
	log_entry = Log(level=level, message=message)
	# Import db lazily to avoid circular import
	from __init__ import db
	db.session.add(log_entry)
	db.session.commit()
	
	timestamp = log_entry.created_at.strftime('%Y-%m-%d %H:%M:%S')
	
	# Only print DEBUG logs if in debug mode
	from config.config import parse_args
	args = parse_args()
	
	if level != "DEBUG" or args.debug:
		print(f"[{level}] | {timestamp} | {message}", flush=True)
		
	return log_entry

# -------------------------------------------------------------------------
# Log retention utility
# -------------------------------------------------------------------------
def prune_logs(older_than_days: int = 90):
	"""
	Delete log entries older than ``older_than_days``.
	"""
	# Import Log model locally to avoid circular imports
	from models.log import Log
	cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=older_than_days)
	try:
		# Import db lazily to avoid circular import
		from __init__ import db
		deleted = Log.query.filter(Log.created_at < cutoff).delete()
		db.session.commit()
		log("INFO", f"Pruned {deleted} log entries older than {older_than_days} days")
	except Exception as e:
		db.session.rollback()
		log("ERROR", f"Failed to prune logs: {str(e)}")