# Symbrex

![rsz_skywatch_ss_ps_20190912t1319_tile_0_0_ohjuabhc_visual-ezgif com-webp-to-jpg-converter](https://github.com/user-attachments/assets/c9bccb14-9d6a-41fd-8d0a-700212c68bc7)

Healthcare supply chain risk management platform. Symbrex utilises hospital usage data (medical equipment usage log) and enhances it with additional metrics (market sentiment, satellite imagery) to provide risk estimates for each hospital supplier, therefore, informing procurement specialist of any potential disruption days in advance. In case of disruption, it also suggest some alternative vendors from NHS-database that are able to supply with the same medical equipment.

## Data
We were able to use real usage dataset from UCLH for fast-moving surgical equipment, but we are not able to share it here (please reach out if interested)

## Model
Symbrex uses the following pathway:
- User inputs usage .csv file containing medical item, its description, manufacturer and it's location (default format)
- We scrape exact coordinates of those manufacturing locations and use google earth engine api to get images of their facilities
- Satellite imagery is used to investigate any damage or change in infrastructure that might affect the supply chain
- This data is then merged with the overall market sentiment of the company and past usage
- Symbrex provides 3 estimate scores between 1 and 10: activity (infrastructure changes, higher is better), confidence (market sentiment, higher is better), risk (lower is better)
- In case risk passes a threshold, we provide a list of alternative suppliers
- Model output is also decribed and provided as an explanation to user increasing explainability
- Most of the analysis is performed using Claude-Sonnet-3.5 (demonstrates best results) due to time constraints
