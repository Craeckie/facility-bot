from matplotlib import pyplot, dates, ticker, rcParams, cm, colors
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap
import numpy as np
import io
from dateutil.rrule import *

rcParams['date.autoformatter.minute'] = '%H:%M'
rcParams['date.autoformatter.hour'] = '%d.%m %Hh'
rcParams['date.autoformatter.day'] = '%d.%m.%y'

def plot(y, xs=None):
    fig, ax = pyplot.subplots(figsize=(15, 8))
    if xs:
      xDates = [dates.date2num(x) for x in xs]
      color_levels = np.linspace(0, 24, 200)
      #ax.plot(xDates, y, marker='o') #, xdate=True)

      # Colormap
      points = np.array([xDates, y]).T.reshape(-1, 1, 2)
      segments = np.concatenate([points[:-1], points[1:]], axis=1)

      lc = LineCollection(segments, cmap=ListedColormap(['r', 'g', 'b']), norm=pyplot.Normalize(0,10))
      lc.set_color('red')
      lc.set_linewidth(2)
      #lc.set_array(color_levels)
      #fig.colorbar(line, ax=ax)

      colormap = colors.LinearSegmentedColormap.from_list('my_temp', 
      [
        (0, 'blue'),
        (17/26, 'lime'),
        (20/26, 'yellow'),
        (1, 'red')
      ], N=300)
      ax.scatter(xDates, y, s=1.5, c=y, vmin=14, vmax=25, cmap=colormap)
      #ax.plot(xDates, y)
      # ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
      # ax.xaxis.set_major_formatter(dates.DateFormatter('%d.%m'))
      locator = dates.AutoDateLocator()
      ax.xaxis.set_major_formatter(dates.AutoDateFormatter(locator))
      # ax.yaxis.set_major_formatter(pyplot.FuncFormatter('{:.0f}'.format))
      ax.yaxis.set_major_formatter(ticker.ScalarFormatter())

      # ax.xaxis.set_major_locator(dates.DayLocator(interval=3))
      # ax.xaxis.set_minor_locator(dates.DayLocator(interval=1))
      ax.xaxis.set_major_locator(locator)
      min_locator = dates.AutoDateLocator()
      min_locator.intervald[MINUTELY] = [1]
      min_locator.intervald[HOURLY] = [1]
      min_locator.intervald[DAILY] = [1]
      min_locator.intervald[MONTHLY] = [1]
      ax.xaxis.set_minor_locator(min_locator)
      #ax.xticks(xDates[0::12])
      #line = ax.add_collection(lc)
    else:
      ax.plot(y)
    #pyplot.axhline(y=19, color='blue')
    pyplot.axhline(y=21, color='green')
    #pyplot.axhline(y=23, color='red')
    ax.set(xlabel='date & time', ylabel='temperature (°C)')
    fig.autofmt_xdate()
    # pyplot.xticks(rotation=90)
    ax.grid()

    buf = io.BytesIO()
    pyplot.savefig(buf, format='png', bbox_inches='tight')
    pyplot.close('all')
    buf.seek(0)
    return buf
