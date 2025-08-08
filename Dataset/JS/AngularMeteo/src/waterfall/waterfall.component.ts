import { ChangeDetectionStrategy, Component, ElementRef, input, signal, ViewChild, ViewEncapsulation } from '@angular/core';
import { ironPalette } from './palette';
import { WaterfallData } from './model';
import { SimpleChanges } from '../types';

interface Range {
  min: number;
  max: number;
}

@Component({
  selector: 'mto-waterfall',
  templateUrl: './waterfall.component.html',
  styleUrl: './waterfall.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.None
})
export class WaterfallComponent {
  public pointWidth = input<number>(7);
  public pointHeight = input<number>(2);
  public palette = input<string[]>(ironPalette); // HEX values only, i.e. #AABBCC
  public timeAxisWidth = input<number>(64);
  public columnAxisHeight = input<number>(16);
  public data = input.required<WaterfallData>();
  public label = input<string>('');

  @ViewChild('waterfallCanvas', { static: true })
  protected waterfallCanvas: ElementRef | undefined;

  protected range = signal<Range | undefined>(undefined);

  public ngOnChanges(changes: SimpleChanges<WaterfallComponent>) {
    if (changes.data && !changes.data.firstChange && this.waterfallCanvas) {
      this.renderData(this.waterfallCanvas.nativeElement);
    }
  }

  public ngAfterViewInit() {
    if (this.waterfallCanvas && this.data()) {
      this.renderData(this.waterfallCanvas.nativeElement);
    }
  }

  private renderData(canvas: HTMLCanvasElement): void {
    canvas.height = this.pointHeight() * this.data().rows.length + this.columnAxisHeight();
    canvas.width = this.pointWidth() * this.data().columnCount + this.timeAxisWidth();
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    if (!ctx) {
      throw new Error('Unexpected: no context.');
    }

    // clear background
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // render data
    const range = this.getRange();
    this.range.set(range);
    const rgbPalette = this.palette().map((c) => this.hexToRGB(c));
    const imageData = ctx.getImageData(
      this.timeAxisWidth(),
      0,
      this.data().columnCount * this.pointWidth(),
      this.data().rows.length * this.pointHeight()
    );
    this.data().rows.forEach((row, rowIndex) => {
      row.forEach((column, columnIndex) => {
        if (!column) {
          return;
        }

        const rgbColor = this.getPointColor(rgbPalette, column, range.max, range.min);
        const pxOffset =
          (rowIndex * this.pointHeight() * this.data().columnCount * this.pointWidth() + columnIndex * this.pointWidth()) *
          4;
        for (let x = 0; x < this.pointWidth(); x++) {
          for (let y = 0; y < this.pointHeight(); y++) {
            const offset = pxOffset + x * 4 + y * this.data().columnCount * this.pointWidth() * 4;
            imageData.data[offset + 0] = rgbColor[0];
            imageData.data[offset + 1] = rgbColor[1];
            imageData.data[offset + 2] = rgbColor[2];
            imageData.data[offset + 3] = 255;
          }
        }
      });
    });
    ctx.putImageData(imageData, this.timeAxisWidth(), 0);

    // render time axis
    const timestamps = this.data().timeLabels;
    for (let i = 0; i < timestamps.length; i++) {
      const timestamp = timestamps[i];
      // text
      if (timestamp) {
        ctx.textBaseline = 'top';
        ctx.fillStyle = 'lightgray';
        ctx.fillText(timestamp, 0, i * this.pointHeight());
      }
      
      // label tick
      const tickWidth = timestamp ? 6 : 2;
      for (let x = this.timeAxisWidth() - tickWidth; x < this.timeAxisWidth(); x++) {
        ctx.fillRect(x, i * this.pointHeight(), 1, 1);
      }
    }

    // render column axis
    const columnLabels = this.data().columnLabels;
    for (let i = 0; i < columnLabels.length; i++) {
      const label = columnLabels[i];
      // text
      if (label) {
        ctx.textBaseline = 'bottom';
        ctx.fillStyle = 'lightgray';
        ctx.fillText(label, this.timeAxisWidth() + i * this.pointWidth(), canvas.height);
      }
      
      // label tick
      const tickHeight = label ? 6 : 2;
      const baseline = this.data().rows.length * this.pointHeight()
      for (let y = baseline; y < baseline + tickHeight; y++) {
        ctx.fillRect(this.timeAxisWidth() + i * this.pointWidth(), y, 1, 1);
      }
    }
  }

  private getRange(): Range {
    const range = {
      min: Infinity,
      max: -Infinity,
    };

    for (var row of this.data().rows) {
      for (var col of row) {
        if (col !== undefined) {
          range.max = Math.max(col, range.max);
          range.min = Math.min(col, range.min);
        }
      }
    }

    return range;
  }

  private hexToRGB(hex: string): number[] {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);

    return [r, g, b];
  }

  private getPointColor(rgbPalette: number[][], value: number, max: number, min: number) {
    const ratio = (value - min) / (max - min);
    const colorIndex = Math.round(ratio * (rgbPalette.length - 1));

    return rgbPalette[colorIndex] || rgbPalette[rgbPalette.length - 1];
  }
}
