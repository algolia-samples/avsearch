import { h, render, Fragment } from 'preact';
import '../util/number.extensions';
import { autocomplete, getAlgoliaResults } from '@algolia/autocomplete-js';
import algoliasearch from 'algoliasearch/lite';
import { createQuerySuggestionsPlugin } from '@algolia/autocomplete-plugin-query-suggestions';
import '@algolia/autocomplete-theme-classic';

const searchClient = algoliasearch(
  'OKF83BFQS4',
  '2ee1381ed11d3fe70b60605b1e2cd3f4'
);

const querySuggestionsPlugin = createQuerySuggestionsPlugin({
  searchClient,
  indexName: 'devcon-22-sessions_query_suggestions',
  getSearchParams({ state }) {
    return { hitsPerPage: state.query ? 3 : 5 };
  },
  transformSource({ source }) {
    return {
      ...source,
      templates: {
        ...source.templates,
        header({ state }) {
          return (
            <Fragment>
              <span className="aa-SourceHeaderTitle">Suggestions</span>
              <div className="aa-SourceHeaderLine" />
            </Fragment>
          );
        },
      },
    };
  },
});

function changeChannel(vidID, time) {
  console.log(vidID);
  document.getElementById('ytVideo').src = "https://www.youtube.com/embed/ISoRfSYRGG0?t=722";
}

const { setIsOpen } = autocomplete({
  container: '#autocomplete',
  detachedMediaQuery: '',
  plugins: [querySuggestionsPlugin],
  openOnFocus: true,
  defaultActiveItemId: 0,
  placeholder: 'Search sessions',
  getSources() {
    return [
      {
        sourceId: 'sessions',
        getItems({ query }) {
          return getAlgoliaResults({
            searchClient,
            queries: [
              {
                indexName: 'devcon-22-sessions',
                query,
                params: {
attributesToSnippet: ['videoTitle:10', 'text:10'],
                  snippetEllipsisText: '…',
                  hitsPerPage: 10,
                  distinct: 2
                }
              }
            ]
          })
        },
        getItemUrl({ item }) {
          return item.url;
        },
        onActive({ item, setContext }) {
          setContext({ preview: item });
        },
        templates: {
          header({ items, state, Fragment }) {
            if (items.length === 0 || state.query === '') {
              return null;
            }

            return (
              <Fragment>
                <span className="aa-SourceHeaderTitle">
                  Sessions
                </span>
                <div className="aa-SourceHeaderLine" />
              </Fragment>
            );
          },
          noResults() {
            return "No sessions match this query.";
          },
          item({ item, state, components }) {
            if (state.query === '') {
              return null;
            }

            return (
              <a className="aa-ItemLink" href={item.url} target="_blank">
                <div className="aa-ItemContent">
                  <div className="aa-ItemIcon">
                    <img
                      src={item.thumbnail}
                      alt={item.videoTitle}
                      width="20"
                      height="20"
                    />
                  </div>
                  <div className="aa-ItemContentBody">
                    <div className="aa-ItemContentTitle">
                      <components.Snippet hit={item} attribute="videoTitle" />
                    </div>
                    <div className="aa-ItemContentDescription">
                      <components.Snippet hit={item} attribute="text" />
                    </div>
                  </div>
                </div>
                <div className="aa-ItemActions">
                  <button
                    className="aa-ItemActionButton aa-DesktopOnly aa-ActiveOnly"
                    id="change-video-${item.ObjectID}"
                    onClick={() => alert(item.videoID)}
                    type="button"
                    title="Watch"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-youtube"><path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.33z"></path><polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02"></polygon></svg>
                  </button>
                </div>
              </a>
            )
          }
        }
      }
    ];
  },
  render({ children, state, Fragment, components }, root) {
    const { preview } = state.context
    render(
      <Fragment>
        <div className="aa-Grid">
          <div className="aa-Results aa-Column">{children}</div>
          {state.query !== '' && 'preview' in state.context && ( 
            <a className="aa-PreviewLink" href={preview.url} target="_blank">
            <div className="aa-Preview aa-Column">
              <div className="aa-PreviewContent">
                <p className="aa-ItemContentDescription">
                  ...{preview.context.before.text} <components.Highlight hit={preview} attribute="text" /> {preview.context.after.text}...
                </p>
              </div>
              <div className="aa-PreviewTitle">
                <components.Snippet hit={preview} attribute="videoTitle" />
              </div>
              <div class="aa-PreviewTimeIcon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-clock"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> 
              </div>
              <div className="aa-PreviewTime">
                {preview.start.toTimeString()}-{preview.end.toTimeString()}
              </div>
              <div className="aa-PreviewImage">
                <img src={preview.thumbnail} alt={preview.videoTitle} />
              </div>
              <div class="aa-PreviewContentSubtitle">
                {preview.categories.join(', ')}
              </div>
            </div>
            </a>
          )}
        </div>
      </Fragment>,
      root
    );
  }
});

document.addEventListener('keydown', (event) => {
  if (event.metaKey && event.key.toLowerCase() === 'k') {
    setIsOpen(true);
  }
});
