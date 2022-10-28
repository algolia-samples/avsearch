import { autocomplete, getAlgoliaResults } from '@algolia/autocomplete-js';
import algoliasearch from 'algoliasearch';
import React, { createElement, Fragment, useEffect, useRef } from 'react';
import { render } from 'react-dom';

const searchClient = algoliasearch(
  process.env.NEXT_PUBLIC_ALGOLIA_APP_ID,
  process.env.NEXT_PUBLIC_ALGOLIA_SEARCH_API_KEY,
);

export default function Autocomplete(props) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) {
      return undefined;
    }

    const search = autocomplete({
      container: containerRef.current,
      renderer: { createElement, Fragment },
      render({ children }, root) {
        render(children, root);
      },
      placeholder: "Search for sessions",
      detachedMediaQuery: '',
      openOnFocus: true,
      getSources({ query, state }) {
        if (!query) {
          return [];
        }

        return [
          {
            sourceId: "sessions",
            getItems() {
              return getAlgoliaResults({
                searchClient,
                queries: [
                  {
                    indexName: process.env.NEXT_PUBLIC_ALGOLIA_INDEX,
                    query,
                    params: {
                      attributesToSnippet: ['videoTitle:10', 'text:20'],
                      snippetEllipsisText: '…',
                      hitsPerPage: 10
                    }
                  }
                ]
              });
            },
            templates: {
              header() {
                return (
                  "Sessions"
                );
              },
              item( {item, components, html }) {
                return html`<div class="aa-ItemWrapper">
                  <a href="${item.url}">
                  <div class="aa-ItemContent">
                    <div class="aa-ItemIcon aa-ItemIcon--alignTop">
                      <img
                        src="${item.thumbnail}"
                        alt="${item.title}"
                        width="80"
                        height="80"
                      />
                    </div>
                    <div class="aa-ItemContentBody">
                      <div class="aa-ItemContentTitle">
                          ${components.Snippet({
                            hit: item,
                            attribute: 'videoTitle',
                          })}
                      </div>
                      <div class="aa-ItemContentSubtitle">
                          ${item.categories}
                      </div>
                      <div class="aa-ItemContentDescription">
                        ${components.Snippet({
                          hit: item,
                          attribute: 'text',
                        })}
                      </div>
                    </div>
                  </div>
                  </a>
                </div>`;
              },
              noResults( ) {
                return "No sessions match this query.";
              }
            },
            getItemUrl({ item }) {
              return item.url;
            }
          }
        ];
      },
      ...props,
    });

    document.addEventListener('keydown', (event) => {
      if (event.metaKey && event.key.toLowerCase() === 'k') {
        search.setIsOpen(true);
      }
    });

    return () => {
      search.destroy();
    };    
  }, [props]);

  return <div ref={containerRef} />;
}
