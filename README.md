# Software Engineering Productivity Metrics

## Guide for Contributing

1. Clone the repo
2. `pip install -r requirements.txt`
3. set the `GH_API_TOKEN` environment variable by running `echo 'export GH_API_TOKEN={YOUR_PERSONAL_TOKEN}' >> ~/.bashrc`. See [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) on how to get a personal token. Note that this commands assume you use bash. use the appropriate config file in place of ~/.bashrc.
4. Before adding/committing any files;
    - Run `pytest test.py` and make sure tests pass.
    - Run `black .` to format your code.
5. After making a pull request, don't attempt to merge unless the check passes, it might take a few seconds for it to show up.
