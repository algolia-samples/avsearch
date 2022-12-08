function changeChannel(container: string, vidID: string, time: number) {
  const url = `https://www.youtube.com/embed/${vidID}?start=${Math.trunc(time)}&autoplay=1`;
  // console.log(url);
  // console.log(container);
  document.getElementById(container).src = url;
}

export function createLoadVideoPlugin(options) {
  return {
    name: 'aa.LoadVideoPlugin',
    subscribe({ onSelect }) {
      onSelect(({ item, state, event }) => {
        if (item.__autocomplete_indexName.endsWith('query_suggestions')) {
          console.log('Query suggestion');
          // event.preventDefault();
          // event.stopPropagation();
          // setQuery(`${item.query} `);
          // refresh();
        }
        else {
          // console.log(item.videoID);
          changeChannel(options.container, item.videoID, item.start);
        }
      });
    },
    __autocomplete_pluginOptions: options,
  };
}

