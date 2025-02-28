# Unlocking the Power of Customer Relations Intelligence

## Step B

- Add the landing page at an appropriate development stage.
- Implement the "Sign in with Google" feature.

## Step C

- Redefine the user information structure to include:
  - Verification Boolean.
  - Time credit tracking.
  - Payment methods.
  - Additional values needed for future functionalities.

- Add new MongoDB collections:
  - **Uploaded Records**: Define records with their associated "Rickets."
  - **Payments History/Log**: Maintain a log of payment transactions.
  - **Events History/Log**: Track user activities and system events.

## Step D

- In the first tab, represent a promise of insightful data visualization after uploading 10 hours of recorded calls:
  - Display a bubble chart of the most frequent words, excluding blacklisted insignificant terms.
  - Enable time-based report generation (e.g., specific months or custom date ranges).
  - Provide one-click access to generate these insights in report format.

## Step E

- Begin development of the call analysis algorithm:
  - (Language recognition method to be added later).
  - Chunk calls by separating them based on silences.
  - Distinguish between speakers and convert their speech into text.
  - Perform sentiment analysis on each chunk.
  - Mark key mentions of words.

- Visualize the call in a linear manner using HTML and JavaScript:
  - Separate different chunks visually.
  - On hover, display:
    - Speaker identity.
    - Transcribed speech.
    - Highlighted keywords.
    - Top three sentiments.
  - Represent critical details and promises in a widget underneath the linear call visualization.

- Use this algorithm as the backbone of APIs accessible via the web interface (“I/O & Search Engine” tab) and the API.

## Step F

- Develop the search engine to locate specific words and hashtags (e.g., #promise, #criticalInfo).
  - Allow search results to be easily converted into PDFs/reports with a single click.

## Step G

- Create an API authentication mechanism for user access.
- Work on proper documentation rendering for the API.
