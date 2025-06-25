import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useCallback, useEffect, useMemo, useState, ReactElement, CSSProperties } from "react"

function MyComponent({args, disabled, theme}: ComponentProps): ReactElement {

  const {activeLink,pages} = args
  const [active_link, setActiveLink] = useState("");
//  console.log(activeLink,pages)

  useEffect(() => {
    Streamlit.setFrameHeight()
//    getLink(activeLink.label)
      Streamlit.setComponentValue(activeLink.label)
      setActiveLink(activeLink.label);
  }, [])

  const editClassLink = (label : string, coffee_break_display: boolean) : string => {
    const classDefault : string = "a a-default"
    const classActive : string = "a a-active"

    if (label === "Coffee Break"){
      return classActive
    }else if(active_link === label && !coffee_break_display){
      return classActive
    }else return classDefault
  }

  const editClassLi = (label: string): string => {
    const classDefault = "breadcrumb-item";
    const classVisited = "breadcrumb-item item-visited";
    const classDisabled = "breadcrumb-item item-disabled";

    // Find the page object with matching label
    const page = pages.find((p: any) => p.label === label);

    if (page && page.visited === 0) {
      return classDisabled;
    } else if (page && page.visited === 1) {
      return classVisited
    }else {
      return classDefault;
    }
  };

  const page = ({ label, coffee_break_display }: { label: string, coffee_break_display: boolean }) : ReactElement => {
    return (
      <li key={label} onClick={() => getLink(label)} className={editClassLi(label)}>
        <a key={"a-"+label} className={editClassLink(label, coffee_break_display)} tabIndex={-1} role="button" aria-disabled="true">{label}</a>
      </li>
    )
  }

  const getLink = (label: string) => {
//    const page = pages.find((p: any) => p.label === label);
//
//    if (page && page.visited === 0) {
//      return;
//    }
//
//    if (active_link === label) return
//
//    Streamlit.setComponentValue(label)
//    setActiveLink(label);
      return
  }

//    <!-- create your own html -->
  return (
    <span>
      <nav aria-label="breadcrumb">
        <ol className="breadcrumb">
          {
            (() => {
              const visiblePages = [];

              const activePageIndex = activeLink.index;
              const activePage = pages.find((p:any) => p.index === activePageIndex);

              const stopAfterActivePage =
                activePage?.coffee_break === true &&
                activePage?.coffee_break_display === true;

              for (const p of pages) {
                if (p.index > activePageIndex && p.coffee_break && p.coffee_break_display) break;

                visiblePages.push(page(p));

                if (stopAfterActivePage && p.index === activePageIndex) {
                  visiblePages.push(page({label: "Coffee Break", coffee_break_display: false}));
                  break;
                }
              }

              return visiblePages;
            })()
          }
        </ol>
      </nav>
    </span>
  )
}

export default withStreamlitConnection(MyComponent)
