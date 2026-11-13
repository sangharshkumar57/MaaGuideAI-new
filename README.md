# MaaGuide AI · Meera’s lunch break
Group 13 | Digital Product Management, Phase 2

## Present the use case in 90 seconds

1. Introduce Meera, a Hyderabad analyst at week 22 of pregnancy. Just before a call, she has mild heartburn and receives her mother's suggestion to try ajwain water.
2. Click **Help Meera decide**. Choose **At my desk now** and review the post-lunch action and its NHS source. Click **Get Gemini’s recommendation** to explain why the action fits Meera’s situation. Select **Choose this plan**.
3. Choose **Telugu** and read the reply. It thanks Amma, reflects the chosen action and explains that Meera will check with her doctor about the remedy. Copy it if desired. Continue with **Keep this reply and check in**.
4. Select how clear the next step feels, finish the check-in and download the takeaway. It includes the selected action, family reply, clinician question and reflection. Restart to try the next-lunch option.

The check-in measures perceived clarity in a fictional walkthrough. No clinical outcome is measured. The app has no database and keeps choices in Streamlit session state. The family reply is copied or downloaded manually.

## Deploy from GitHub on Windows

1. Extract the ZIP. Create a GitHub repository, for example maaguidedemo, with main as its default branch.
2. Open the repository. Use **uploading an existing file** (empty repository) or **Add file → Upload files**. Drag the extracted app.py, requirements.txt, README.md and .streamlit folder into the upload area. Commit to main. If the folder is skipped, create .streamlit/config.toml using Add file → Create new file and paste its contents. The theme is optional.
3. Open https://share.streamlit.io and connect your GitHub account. Choose **Create app → Yup, I have an app**. Select the repository, branch main and entrypoint app.py. Choose Python 3.12 under Advanced settings. Deploy.
4. Open the assigned streamlit.app URL and follow the four steps above. Secrets are optional. If Cloud cannot find the entrypoint, check that app.py and requirements.txt are directly in the repository root.
5. Commit later edits to the same branch to update the app.

## Enable Gemini recommendations

Create a key in [Google AI Studio](https://aistudio.google.com/apikey). For an existing deployment open app settings → Secrets; during a new deployment use Advanced settings → Secrets. Save this TOML with your actual key:

```toml
GEMINI_API_KEY = "your-key-here"
GEMINI_MODEL = "gemini-flash-latest"
```

For local use, place these values in .streamlit/secrets.toml and keep the file off GitHub. The model is configurable; if the alias is unavailable, use a generateContent model ID enabled for the key. No SDK dependency is required.

On step 2 choose a timing and click **Get Gemini’s recommendation**. The server sends the fictional scenario, timing, selected action, and fixed NHS guidance notes to Gemini. The explanation is saved for that timing in the session and included in the takeaway for the chosen plan. Failed calls show a setup or retry message. The app keeps the built-in plan available. Step 3 also supports suggesting a family reply opener.

## Local launch

From the extracted folder with Python 3.12 installed:

    py -3.12 -m venv .venv
    .venv\Scripts\python -m pip install -r requirements.txt
    .venv\Scripts\python -m streamlit run app.py

Sources: [NHS pregnancy heartburn guidance](https://www.nhs.uk/pregnancy/common-symptoms/indigestion-and-heartburn/) · [Streamlit deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
