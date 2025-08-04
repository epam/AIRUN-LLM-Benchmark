import { Injectable } from '@angular/core';
import { fetchWeatherApi } from 'openmeteo';
import { WeatherApiResponse } from '@openmeteo/sdk/weather-api-response';
import { WeatherPoint, WeatherTimeseries } from './model';

@Injectable({
  providedIn: 'root',
})
export class MeteoDataService {
  private readonly forecastApiUrl = 'https://api.open-meteo.com/v1/forecast';
  private readonly archiveApiUrl = 'https://archive-api.open-meteo.com/v1/archive';

  public async getForecastTimeseries(latitude: number, longitude: number, timezone: string, forecastDays: number, pastDays: number): Promise<WeatherTimeseries> {
    const params = {
      'latitude': latitude,
	    'longitude': longitude,
	    'hourly': [
        'temperature_2m',
        'relative_humidity_2m',
        'precipitation',
        'wind_speed_10m',
        'surface_pressure',
      ],
	    'timezone': timezone,
	    'past_days': pastDays,
	    'forecast_days': forecastDays
    }

    const responses = await fetchWeatherApi(this.forecastApiUrl, params);
    return this.processResponses(responses);
  }  

  public async getArchiveTimeseries(latitude: number, longitude: number, timezone: string, startDate: string, endDate: string): Promise<WeatherTimeseries> {
    const params = {
      'latitude': latitude,
	    'longitude': longitude,
	    'hourly': [
        'temperature_2m',
        'relative_humidity_2m',
        'precipitation',
        'wind_speed_10m',
        'surface_pressure',
      ],
	    'timezone': timezone,
	    'start_date': startDate,
	    'end_date': endDate
    }

    const responses = await fetchWeatherApi(this.archiveApiUrl, params);
    return this.processResponses(responses);
  }

  private processResponses(responses: WeatherApiResponse[]): WeatherTimeseries {
    const response = responses[0];
    if (!response) {
      throw new Error('No response from weather API');
    }

    const timeseries: WeatherTimeseries = {
      lat: response.latitude(),
      lon: response.longitude(),
      utcOffset: response.utcOffsetSeconds(),
      points: []
    };
    const hourlyData = response.hourly();
    if (!hourlyData) {
      throw new Error('Hourly data is not available');
    }
    const temp2m = hourlyData.variables(0)?.valuesArray();
    if (!temp2m) {
      throw new Error('Temperature data is not available');
    }
    const humidity2m = hourlyData.variables(1)?.valuesArray();
    if (!humidity2m) {
      throw new Error('Humidity data is not available');
    }
    const precipitation = hourlyData.variables(2)?.valuesArray();
    if (!precipitation) {
      throw new Error('Precipitation data is not available');
    }
    const windSpeed10m = hourlyData.variables(3)?.valuesArray();
    if (!windSpeed10m) {
      throw new Error('Wind speed data is not available');
    }
    const surfacePressure = hourlyData.variables(4)?.valuesArray();
    if (!surfacePressure) {
      throw new Error('Surface pressure data is not available');
    }

    const endTime = Number(hourlyData.timeEnd());
    const startTime = Number(hourlyData.time());
    const interval = hourlyData.interval();
    const pointsCount = (endTime - startTime) / interval;
    for (let i = 0; i < pointsCount; i++) {
      const point: WeatherPoint = {
        localTime: startTime + i * interval,
        temp2m: isNaN(temp2m[i]) ? undefined : temp2m[i],
        relHumidity2m: isNaN(humidity2m[i]) ? undefined : humidity2m[i],
        precipitation: isNaN(precipitation[i]) ? undefined : precipitation[i],
        windSpeed10m: isNaN(windSpeed10m[i]) ? undefined : windSpeed10m[i],
        surfacePressure: isNaN(surfacePressure[i]) ? undefined : surfacePressure[i],
      };

      timeseries.points.push(point);
    }

    return timeseries;
  }
}