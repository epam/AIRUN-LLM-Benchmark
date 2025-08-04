import { Injectable } from '@angular/core';
import { ItemLocation } from './model';

@Injectable({
  providedIn: 'root',
})
export class GeoLocationDataService {
  public async searchLocations(term: string): Promise<ItemLocation[]> {
    const data = [
      { name: 'Minsk', latitude: 53.9, longitude: 27.5667 },
      { name: 'Gomel', latitude: 52.4345, longitude: 30.9754 },
      { name: 'Mogilev', latitude: 53.9045, longitude: 30.3456 },
      { name: 'Vitebsk', latitude: 55.1894, longitude: 30.1994 },
      { name: 'Grodno', latitude: 53.6667, longitude: 23.8333 },
      { name: 'Brest', latitude: 52.0975, longitude: 23.7036 },
    ];
    const result = data.filter(item =>
      item.name.toLowerCase().includes(term.toLowerCase())
    );

    return new Promise(resolve => {
      setTimeout(() => {
        resolve(result);
      }, 1000);
    });
  }
}