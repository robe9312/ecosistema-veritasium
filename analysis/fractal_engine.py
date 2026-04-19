import polars as pl
import numpy as np
import sys
import json
import urllib.request
from scipy.stats import linregress, kurtosis

def get_fear_and_greed():
    """Fetches current sentiment token from Alternative.me"""
    try:
        req = urllib.request.urlopen("https://api.alternative.me/fng/?limit=1", timeout=5)
        res = json.loads(req.read())
        data = res['data'][0]
        return data['value_classification'], int(data['value'])
    except Exception as e:
        return "Unknown", 50

def calculate_hurst_dynamic(prices, min_lag=2, max_lag=100):
    """
    Calculates the Hurst Exponent using the variance of lagged differences.
    H > 0.5: Persistent (Trending)
    H < 0.5: Anti-persistent (Mean Reverting)
    H = 0.5: Random Walk
    """
    series = np.log(prices)
    lags = range(min_lag, max_lag)
    tau = []
    std_diff = []
    
    for lag in lags:
        # standard deviation of lagged differences
        diff = series[lag:] - series[:-lag]
        tau.append(lag)
        std_diff.append(np.std(diff))
        
    # Slope of log-log plot
    reg = linregress(np.log(tau), np.log(std_diff))
    return reg.slope

def analyze_criticality(data_json):
    """
    Analyzes a list of prices to detect 'Self-Organized Criticality'.
    Incorporates Market Sentiment for 'Zero Claw' confidence scoring.
    """
    try:
        data = json.loads(data_json)
        prices = np.array(data['prices'], dtype=np.float64)
        
        if len(prices) < 100:
            return {"error": "Insufficient data (min 100 candles required)"}
            
        # 1. Hurst Exponent (Window: 100)
        h_val = calculate_hurst_dynamic(prices[-100:])
        
        # 2. Kurtosis (Heavy tails detection)
        # Financial returns are often leptokurtic (Kurtosis > 3)
        returns = np.diff(prices) / prices[:-1]
        kurt_val = kurtosis(returns)
        
        # 3. Detect Criticality (Sudden drop in Hurst from >0.5)
        # We compare the current H with the H from 20 periods ago
        h_prev = calculate_hurst_dynamic(prices[-120:-20]) if len(prices) >= 120 else h_val
        
        is_critical = False
        confidence = 0.0
        
        if h_prev > 0.55 and h_val <= 0.51:
            is_critical = True # Power law 'avalanche' potential
            # Calculate a base confidence based on drop severity and kurtosis
            drop_factor = min(1.0, max(0.0, (0.55 - h_val) / 0.15)) 
            kurt_factor = min(1.0, max(0.0, (kurt_val - 3) / 10))
            base_confidence = (drop_factor * 0.6) + (kurt_factor * 0.4)
            confidence = base_confidence
            
        # 4. Sentiment Synergy
        sentiment_class, sentiment_val = get_fear_and_greed()
        
        if is_critical:
            if sentiment_val <= 25 or sentiment_val >= 75: # Extreme Fear or Extreme Greed
                confidence = min(0.99, confidence + 0.25) # Boost confidence
            elif 25 < sentiment_val <= 45 or 55 <= sentiment_val < 75:
                confidence = min(0.99, confidence + 0.10)
                
        signal = "ACTIVATE" if is_critical and kurt_val > 5 else "WAIT"
        
        # ZERO CLAW OVERRIDE
        if confidence >= 0.9:
            signal = "ZERO_CLAW_ATTACK"

        return {
            "hurst": round(h_val, 4),
            "kurtosis": round(kurt_val, 4),
            "is_critical": is_critical,
            "sentiment": sentiment_class,
            "sentiment_score": sentiment_val,
            "confidence_score": round(confidence, 4),
            "signal": signal
        }
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No input data provided"}))
        sys.exit(1)
        
    result = analyze_criticality(sys.argv[1])
    print(json.dumps(result))
