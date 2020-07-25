INWX hook for dehydrated
---

You need to add a configuration file called "inwx-config" into "/etc/dehydrated/" folder or place it right next to the python script.

Add your INWX credentials to the file:

```
[user]
username = 
password = 
```

Install dependencies with pip `pip install -r requirements.txt`.
I recommend using a virtualenv.

I also added a hook.sh script, which is optional but may help to prevent globbing and word splitting.
