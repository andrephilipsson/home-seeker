# Home seeker
A Python script that checks for available apartments on AF Bostäder.

## Configuration
The configuration is very limited, and you will need to have some knowledge of Python if you want to create custom filters.

### Receive email
By default the program will send the results to stdout (print it to the terminal). If you would want to receive an email notification with the apartments you will have to change the `config.json` file. If you use Gmail, the configuration for that can be found [here](https://support.google.com/mail/answer/7126229).

Default `config.json`: 

```json
{
  "email": "example@example.com",
  "password": "supersecretpassword",
  "port": 587,
  "smtpServer": "smtp.example.com",
  "sendEmail": false  // change this to true to enable emails
}
```

### Custom filters
Custom filters can be added to the `filter_apartments()` function. Here is an example that *excludes* "Korridorrum":

```python
def filter_apartments(apts):
    filtered_apts = []
    for apt in apts:
        # This is where you would add your own filters
        if apt["type"] != "Lägenhet":
            continue

        filtered_apts.append(apt)

    return filtered_apts
```

## Tips
The script is preferably run with a cronjob. If you have no idea what a cronjob is, check out this [video](https://www.youtube.com/watch?v=QZJ1drMQz1A).
