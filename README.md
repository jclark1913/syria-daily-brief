
# Syria Daily Brief

SDB is a web scraper designed to gather posts, articles and press announcements from a variety of Arabic-language sources run by governments, non-state actors and independent press. This project is designed to complement the work of Syria-focused analysts, particularly those who deal with large quantities of open-source data.

This repo contains the Flask backend for Syria Daily Brief. You can view the React frontend [here](https://github.com/jclark1913/sdb-frontend)

You can read more about the project [here](#about), or you can find a quickstart guide [here](#quickstart)

<p align="center">
	<img alt="saved_collections" width="500"src="docs/images/saved_collections.png">
	<img alt="entries_list" width="500"src="docs/images/entries_list.png">
	<img alt="entry_detail" width="500"src="docs/images/entry_detail.png">
</p>

This project is in active development and updated regularly with new features and improvements.

## About


### Why?

Tracking news and press releases is time-consuming, particularly when dealing with press releases and propaganda from the regime and non-state actors. As a former analyst and perennial Syria-watcher, I want to build tools that ease this process - to streamline the gathering, translating and curating of data so more time can be spent analyzing trends and sentiments rather than monitoring social media feeds.

The app features a backend API written in Flask/python and a frontend UI build in React/Javascript/TailwindCSS.

### Core Features & Roadmap

- Collect data from a spectrum of Arabic-language websites
	[x] Choose how far back you'd like to gather data and from which sources (Last 24 hrs, last week, last 6 months, etc)
	[x] Gather data from a single source based on parameters you provide or cast a wide net to all available sources.
	[] Scrape data from more than a dozen Syria-focused websites
- Manage collected data
	[x] Explore collected data through responsive UI
	[] Search, tag and filter entries depending on your content
	[x] Export data to .csv, .xlsx formats
- Machine translations and summaries
	[x] Get English-language summaries from the OpenAI API
	[x] Get quick machine translations from the ArgosTranslate API
- Use responsive UI to edit, view and manage data
	[x] Save scraped data to personalized collections
	[x] View entries in sortable, editable database
	[] Search data and tag entries of interest
	[] Personalize data collection operations from frontend


### Contact

To report issues, suggest a feature, request to be a contributor or ask about the project please contact me at jclarksummit@gmail.com.

## Quickstart

This project is currently in active development and there is no stable release. Check back soon!
