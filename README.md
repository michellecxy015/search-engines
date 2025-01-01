# Search Engine Harmful Content Filtering Analysis

## Overview

This project evaluates the effectiveness of mainstream search engines (Google, Bing, and Kiddle) in filtering harmful content through image search results. The study involves scraping images using predefined search queries combined with harmful keywords and analyzing the content using the CLIP model. The goal is to assess how well search engines filter inappropriate content, compare their filtering approaches, and understand how SafeSearch settings affect the outcomes.

---

## Workflow

### 1. **Scraping Images**
- Scrapes images from search engines (Google, Bing, and Kiddle) based on predefined search queries:
  - Queries cover **four categories**: Games, Disney Movies, Toys, and Cartoons.
  - Combined with **three types of harmful keywords**: Violence, Sexual Content, and Shock/Disgusting.
- Captures images with SafeSearch enabled and disabled (for Google and Bing).
- Uses Selenium to automate the scraping process and saves the collected images for further analysis.

### 2. **Image Classification**
- Utilizes the CLIP model to classify scraped images into four categories:
  - **Safe for Children**
  - **Violence**
  - **Sexual Content**
  - **Scary or Shocking**
- Performs statistical analysis on the classified data:
  - **Data Distribution**: Compares the volume of harmful vs. safe content across search engines.
  - **Harm Proportion by Search Query**: Evaluates the likelihood of harmful content for different search terms.
  - **Exposure Rate by Position**: Analyzes the placement of harmful images on search result pages.

---

## Research Questions

This project seeks to address the following:
1. How effective are different search engines at filtering harmful content?
2. Are there noticeable differences in filtering approaches between search engines?
3. How do search engine safety settings affect the outcomes?

---

## Results and Findings
- A comparative analysis of Google, Bing, and Kiddle shows varying levels of filtering effectiveness:
  - Kiddle applies stricter keyword-based filtering but still has a high proportion of harmful content, particularly for **Sexual Content**.
  - Bing SafeSearch consistently outperforms the other search engines in filtering harmful content both quantitatively and qualitatively.
  - Google SafeSearch is effective but results in a higher proportion of harmful content compared to Bing.

- **Exposure Rate**: Harmful content often appears in prominent positions (e.g., top-center), increasing the likelihood of user exposure.

---

## Future Work
- Explore the use of additional models for more refined content classification.
- Investigate the impact of more complex queries or user behavior (e.g., misspellings).
- Develop recommendations for improving SafeSearch mechanisms.

---

## How to Use
Take Kiddle as example, the other two search engines folows a simiar workflow except for turning on and off safeSearch.
1. **Scrape Images**: run the `kiddle_scrape.ipynb` notebook to collect Kiddle.
2. **Classify and Analyze**: Use the `kiddle_clip.ipynb` notebook to classify the images and generate comparative statistics.
3. **Customize Queries**: Modify the predefined search queries or harmful keywords as needed to adapt the analysis.

---
