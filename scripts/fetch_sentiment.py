import json
import urllib.request

def fetch_sentiment():
    print("📡 Fetching Market Sentiment (Fear & Greed Index)...")
    try:
        req = urllib.request.urlopen("https://api.alternative.me/fng/?limit=1", timeout=5)
        res = json.loads(req.read())
        data = res['data'][0]
        sentiment_class = data['value_classification']
        sentiment_score = int(data['value'])
        
        output = {
            "sentiment": sentiment_class,
            "score": sentiment_score
        }
        
        print(f"✅ Market Sentiment: {sentiment_class} (Score: {sentiment_score})")
        return output
    except Exception as e:
        print(f"❌ Error fetching sentiment: {e}")
        return {"sentiment": "Unknown", "score": 50}

if __name__ == "__main__":
    result = fetch_sentiment()
    # Escribir a un archivo para que openfang o scripts auxiliares lo puedan consumir fácilmente si se desea
    with open(".veritasium/current_sentiment.json", "w") as f:
        json.dump(result, f, indent=4)
