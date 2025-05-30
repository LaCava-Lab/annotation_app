import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useCallback, useEffect, useMemo, useState, ReactElement, CSSProperties } from "react"

function MyComponent({args, disabled, theme}: ComponentProps): ReactElement {

  const {links, activeLink,pages} = args
  const [active_link, setActiveLink] = useState("");

  useEffect(() => {
    Streamlit.setFrameHeight()
//    getLink(activeLink.label)
      Streamlit.setComponentValue(activeLink.label)
      setActiveLink(activeLink.label);
  }, [])

  const editClassLink = (label : string) : string => {
    const classDefault : string = "a a-default"
    const classActive : string = "a a-active"

    if(active_link === label){
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

  const link = ({ label }: { label: string }) : ReactElement => {
    return (
      <li key={label} onClick={() => getLink(label)} className={editClassLi(label)}>
        <a key={"a-"+label} className={editClassLink(label)} tabIndex={-1} role="button" aria-disabled="true">{label}</a>
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
          {links.map(link)}
        </ol>
      </nav>
    </span>
  )
}

export default withStreamlitConnection(MyComponent)
