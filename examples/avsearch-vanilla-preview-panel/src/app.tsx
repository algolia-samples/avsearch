/** @jsx h */
import './string.extensions'
import { autocomplete, getAlgoliaResults } from '@algolia/autocomplete-js';
import algoliasearch from 'algoliasearch/lite';
import { h, render } from 'preact';

import '@algolia/autocomplete-theme-classic';

const searchClient = algoliasearch(
  'OKF83BFQS4',
  '2ee1381ed11d3fe70b60605b1e2cd3f4'
);

const { setIsOpen } = autocomplete({
  container: '#autocomplete',
  detachedMediaQuery: '',
  openOnFocus: true,
  defaultActiveItemId: 0,
  placeholder: 'Search Sessions',
  getSources({ query, state }) {
    if (!query) {
      return [];
    }

    return [
      {
        sourceId: 'hits',
        getItems({ query }) {
          return getAlgoliaResults({
            searchClient,
            queries: [
              {
                indexName: 'devcon-22-sessions',
                query,
                params: {
                  attributesToSnippet: ['videoTitle:10', "text:20"],
                  snippetEllipsisText: '…',
                  hitsPerPage: 10,
                  distinct: 3
                }
              }
            ]
          });
        },
        getItemUrl({ item }) {
          return item.url;
        },
        onActive({ item, setContext }) {
          setContext({ preview: item });
        },
        templates: {
          header() {
            return <span className='aa-SourceHeaderTitle'>Sessions</span>;
          },
          item({ item, components }) {
            return (
              <a className='aa-ItemLink' href={item.url}>
                <div className='aa-ItemContent'>
                  <div className='aa-ItemIcon'>
                    <img
                      src={item.thumbnail}
                      alt={item.name}
                      width='40'
                      height='40'
                    />
                  </div>
                  <div className='aa-ItemContentBody'>
                    <div className='aa-ItemContentTitle'>
                      <components.Snippet hit={item} attribute='videoTitle' />
                    </div>
                  </div>
                </div>
              </a>
            );
          }
        }
      }
    ];
  },
  render({ children, state, Fragment, components }, root) {
    const { preview } = state.context;
    if (!preview) {
      render(
        <Fragment>
          <div className='aa-Grid'>
            <div className='aa-Results aa-Column'>{children}</div>
          </div>
        </Fragment>,
        root
      );
    } else {
      render(
        <Fragment>
          <div className='aa-Grid'>
            <div className='aa-Results aa-Column'>{children}</div>
            {state.query !== '' && (
              <div className='aa-Preview aa-Column'>
                <div className='aa-PreviewImage'>
                  <img src={preview.thumbnail} alt={preview.videoTitle} />
                </div>
                <div className='aa-PreviewTitle'>
                  <components.Snippet hit={preview} attribute='videoTitle' />
                </div>
                <div className='aa-PreviewTime'>
                  {preview.start.toTimeString()}-{preview.end.toTimeString()}
                </div>
                <div class='aa-PreviewContentSubtitle'>
                  {preview.categories.join(', ')}
                </div>
                <hr />
                <div className='aa-ItemContentDescription'>
                  <components.Highlight hit={preview} attribute='text' />
                </div>
              </div>
            )}
          </div>
        </Fragment>,
        root
      );
    }
  }
});

document.addEventListener('keydown', (event) => {
  if (event.metaKey && event.key.toLowerCase() === 'k') {
    setIsOpen(true);
  }
});
