# Flight Delay Analytics Engine | Airline Operations Intelligence

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Automation](https://img.shields.io/badge/Excel-Report_Generation-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)](https://www.python.org/)
[![IATA](https://img.shields.io/badge/IATA_Standards-Compliant-blue?style=for-the-badge)]()

## Executive Summary

**Flight Delay Analytics Engine** is an automated data processing system that transforms raw airline operational data into actionable business intelligence. Designed for airport handling companies and airline operations, it provides precise delay analysis, handling cost attribution, and automated reporting compliant with IATA standards.

## Business Value Proposition

- **98% Reduction** in manual data processing time
- **Accurate Handling Cost Allocation** through intelligent delay code analysis  
- **Automated Multi-Airline Reporting** with carrier-specific business rules
- **Revenue Protection** via precise surcharge calculation and validation

## Technical Architecture

### Data Processing Pipeline
Raw Data     → Normalization     → Business Logic     → Multi-Format Reporting
TXT/TSV       Column Mapping      Airline Rules        Excel + Analytics

### Core Features
- **Intelligent Data Normalization**: Automatic conversion of multi-format timestamps and airline codes
- **Carrier-Specific Business Logic**: Custom rules for Delta, United, Etihad, and regional carriers
- **Handling Cost Isolation**: Automated filtering of handling-related delay codes (12, 13, 15, 18, 31-35, 39, 52)
- **Multi-Timeframe Analysis**: Cross-month arrival/departure pairing for accurate turnaround analysis

## Key Analytics Capabilities

### Delay Intelligence
- **Real Delay Calculation**: DLY_REAL = max(minutes(ATD - STD), 0)
- **Handling-Free Metrics**: DLY_WO_HNDLG excludes carrier-non-responsible delays
- **Early Arrival Analysis**: ADV_IN = max(minutes(STA - ATA), 0)

### Airline-Specific Modules

| Airline | Key Metrics | Business Rules |
|---------|-------------|----------------|
| **Delta** | Surcharge Calculation | 30%/15% based on delay >180min + time window |
| **United** | Turn Rate Analysis | Progressive % calculation for delays/advances |
| **Etihad** | Performance Flagging | Highlight delays >60 minutes |
| **Regional** | Custom Surcharges | Tiered systems (20%/30%/45%) |

## Operational Impact

### Before
- Manual data processing: 45-60 minutes daily
- Human error in delay code attribution
- Inconsistent reporting across airlines
- Delayed billing for handling services

### After  
- Fully automated processing: <2 minutes
- Standardized IATA-compliant calculations
- Consistent multi-carrier reporting
- Real-time surcharge identification

## Technical Implementation

### Data Normalization Engine
```
def load_txt_to_df(file_path: str) -> pd.DataFrame:
    # Automated column mapping & type conversion
    # Cross-month arrival/departure pairing
    # IATA code standardization
```

### Modular Rule System
```
# Carrier-specific business logic
CNA_rules.delta(df)      # Surcharge calculations
CNA_rules.united(df)     # Turn rate analysis  
CNA_rules.ritardo_generico(df, "CZ", 120)  # Custom thresholds
```

## Sample Output Structure

| Report | Metrics | Business Use |
|--------|---------|--------------|
| Delays_DELTA.xlsx | Surcharge %, Time Windows | Billing Validation |
| Delays_UNITED.xlsx | Turn Rates, Info Required | Operational Efficiency |
| Delays_ARKIA.xlsx | Tiered Surcharges | Revenue Recovery |

## Why This Matters

This system demonstrates enterprise-grade data governance by:
- Transforming operational chaos into structured business intelligence
- Implementing carrier-specific data contracts through rule-based processing
- Providing audit-ready documentation for handling cost disputes
- Establishing scalable framework for additional airline integrations

This system can be customized for specific airline partnerships and operational requirements.
