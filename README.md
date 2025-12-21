# Serverless Grid Compliance Pipeline (VDE-AR-N 4110)

![Python](https://img.shields.io/badge/Python-3.9-blue)
![AWS](https://img.shields.io/badge/AWS-Serverless-orange)
![Pandapower](https://img.shields.io/badge/Grid-Pandapower-green)
![Status](https://img.shields.io/badge/Status-Prototype-yellow)

## Project Overview
This project demonstrates a **Cloud-Native approach to Automated Grid Compliance**. Instead of running manual load flows on desktop software, this pipeline automatically ingests grid models, performs physics-based simulations in the cloud, and validates results against German Grid Codes (**VDE-AR-N 4110**).

It addresses the industry need for **"Cloud-Bursting"**, leveraging **AWS Lambda** to handle peak simulation loads during Redispatch 3.0 calculations without maintaining expensive on-premise hardware.

## Architecture
**Data Flow:**
1.  **Ingest:** Grid models (JSON/Pandapower format) are uploaded to an **AWS S3** Bucket.
2.  **Trigger:** The upload event triggers an **AWS Lambda** function.
3.  **Simulation:** The Lambda function:
    * Loads the grid topology using `pandapower`.
    * Runs a Newton-Raphson Power Flow calculation.
    * Checks node voltages against the $\pm 10\%$ tolerance band defined in **VDE-AR-N 4110**.
4.  **Storage:** Simulation results and violation flags are stored in **Amazon DynamoDB** for auditing.

## Tech Stack
* **Grid Logic:** Python, Pandapower, NumPy
* **Cloud Infrastructure:** AWS Lambda, S3, DynamoDB
* **Infrastructure as Code:** Boto3 (Python SDK)

## Key Features
* **Automated Physics:** Runs full AC Power Flow (not just DC approximation).
* **Regulatory Compliance:** Hard-coded logic for VDE 4110 voltage stability checks ($0.90 < V_{pu} < 1.10$).
* **Scalability:** Capable of processing hundreds of grid scenarios in parallel using Serverless concurrency.

## Future Roadmap (Redispatch 3.0)
* Integration with **AWS Kinesis** for streaming smart meter data.
* Expansion of compliance checks to include line loading (thermal limits).
* Automated generation of "Traffic Light" (Ampelphasen) signals for DSO control rooms.

---
*Created by [Clifford Ondieki](https://www.cliffordomari.com) - Power Systems Engineer & Grid Data Architect*
