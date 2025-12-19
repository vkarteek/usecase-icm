// tools/weather.js
import fetch from "node-fetch";

export async function getWeatherHandler({ city }) {
  if (!city) {
    return {
      content: [
        { type: "text", text: "No city provided." }
      ]
    };
  }

  const url = `http://wttr.in/${encodeURIComponent(city)}?format=j1`;

  try {
    const res = await fetch(url);

    if (!res.ok) {
      return {
        content: [
          { type: "text", text: `Weather API returned HTTP ${res.status}` }
        ]
      };
    }

    const j = await res.json();
    const cur = j.current_condition?.[0];

    if (!cur) {
      return {
        content: [
          { type: "text", text: `No weather data available for ${city}.` }
        ]
      };
    }

    // Build clean text message
    const textMessage = 
      `Weather in ${city}: ${cur.temp_C}°C, feels like ${cur.FeelsLikeC}°C, ` +
      `humidity ${cur.humidity}%, wind ${cur.windspeedKmph} km/h`;

    // Full structured result
    const dataMessage = {
      city,
      temperature: cur.temp_C,
      feels_like: cur.FeelsLikeC,
      humidity: cur.humidity,
      wind_speed_kmph: cur.windspeedKmph,
      weather_desc: cur.weatherDesc?.[0]?.value || ""
    };

    return {
      content: [
        { type: "text", text: textMessage },
        { type: "data", data: dataMessage }
      ]
    };

  } catch (err) {
    return {
      content: [
        { type: "text", text: `Weather fetch error: ${err.message}` }
      ]
    };
  }
}
