export interface WeatherPoint {
  localTime: number; // unix
  temp2m?: number;
  relHumidity2m?: number;
  precipitation?: number;
  windSpeed10m?: number;
  surfacePressure?: number;
}

export interface WeatherTimeseries {
  lat: number;
  lon: number;
  utcOffset: number;
  points: WeatherPoint[];
}

export interface ItemLocation {
  name: string;
  latitude: number;
  longitude: number;
}