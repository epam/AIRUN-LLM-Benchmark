import { ChangeDetectionStrategy, ChangeDetectorRef, Component, inject, output, ViewEncapsulation } from '@angular/core';
import { WaterfallData } from '../waterfall/model';
import { MeteoDataService } from '../data/meteo-data.service';
import { ItemLocation, WeatherPoint, WeatherTimeseries } from '../data/model';
import { WaterfallComponent } from '../waterfall/waterfall.component';
import { FormsModule } from '@angular/forms';
import { AutocompleteComponent } from '../controls/autocomplete/autocomplete.component';
import { AutocompleteDatasource, AutocompleteItem } from '../controls/autocomplete/model';
import { GeoLocationDataService } from '../data/geo-location-data.service';
import { InputComponent } from '../controls/input/input.component';
import { ButtonComponent } from '../controls/button/button.component';

@Component({
  selector: 'mto-historical',
  templateUrl: './historical.component.html',
  styleUrl: './historical.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.None,
  imports: [WaterfallComponent, AutocompleteComponent, InputComponent, ButtonComponent, FormsModule]
})
export class HistoricalComponent {
  private readonly meteoDataService = inject(MeteoDataService);
  private readonly geoLocationDataService = inject(GeoLocationDataService);
  private readonly cdr = inject(ChangeDetectorRef);

  public loading = output<boolean>();
  public error = output<Error>();

  protected latitude = 53.9;
  protected longitude = 27.5667;
  protected timezone = 'Europe/Moscow';

  protected temp2m: WaterfallData | undefined;
  protected relHumidity2m: WaterfallData | undefined;
  protected precipitation: WaterfallData | undefined;
  protected windSpeed10m: WaterfallData | undefined;
  protected surfacePressure: WaterfallData | undefined;

  protected autocompleteLoading = false;
  protected autocompleteError: Error | undefined;
  protected locationDatasource: AutocompleteDatasource<ItemLocation> = {
    search: async (term: string): Promise<AutocompleteItem<ItemLocation>[]> => {
      return await this.geoLocationDataService.searchLocations(term)
        .then((locations) => 
          locations.map((location) => ({
            label: location.name,
            value: location
          })
        )
      );
    }
  };

  public async ngOnInit() {
    this.fetchHistoricalData();
  }

  protected async fetchHistoricalData() {
    this.loading.emit(true);
    try {
      const data = await this.meteoDataService.getArchiveTimeseries(this.latitude, this.longitude, this.timezone, '2024-01-01', '2025-01-01');
      this.processData(data);
    } catch (e) {
      this.error.emit(e as Error)
    } finally {
      this.loading.emit(false);
    }
    
    this.cdr.detectChanges();
  }

  protected onLocationSelected(location: ItemLocation | undefined) {
    if (!location) {
      return;
    }

    this.latitude = location.latitude;
    this.longitude = location.longitude;
  }

  private processData(data: WeatherTimeseries): void {
    this.temp2m = this.createWaterfall(data, 'temp2m');
    this.relHumidity2m = this.createWaterfall(data, 'relHumidity2m');
    this.precipitation = this.createWaterfall(data, 'precipitation');
    this.windSpeed10m = this.createWaterfall(data, 'windSpeed10m');
    this.surfacePressure = this.createWaterfall(data, 'surfacePressure');
  }

  private createEmptyWaterfall(): WaterfallData {
    return {
      columnCount: 24,
      rows: [],
      timeLabels: [],
      columnLabels: Array(24).fill('').map((_, index) => index % 6 === 0 ? `${index}h` : ''),
    };
  }

  private createWaterfall(data: WeatherTimeseries, key: keyof WeatherPoint): WaterfallData {
    const waterfallData = this.createEmptyWaterfall();

    let currDayOfMonth = new Date(data.points[0].localTime * 1000).getDate() - 1;
    for (let i = 0; i < data.points.length; i++) {
      const point = data.points[i];
      const date = new Date(point.localTime * 1000);
      const dayOfMonth = date.getDate();
      if (dayOfMonth !== currDayOfMonth) {
        waterfallData.rows.push(Array(24).fill(undefined));

        let timeLabel = '';
        if (i % 5 === 0) {
          timeLabel = new Date(date.valueOf() + data.utcOffset * 1000).toISOString().split('T')[0];
        }
        waterfallData.timeLabels.push(timeLabel);

        currDayOfMonth = dayOfMonth;
      }      

      const hour = date.getHours();
      waterfallData.rows[waterfallData.rows.length - 1][hour] = point[key];
    }

    return waterfallData;
  }
}
