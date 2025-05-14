import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useCallback, useEffect, useMemo, useState, ReactElement, CSSProperties } from "react"

function MyComponent({args, disabled, theme}: ComponentProps): ReactElement {

  const {links} = args
  let activeLink : String = ""

  useEffect(() => {
    Streamlit.setFrameHeight()
    getLink(links[0].label)
  }, [])

  const editClassLink = (label : string) : string => {
    const classDisable : string = "a"
    const classDefault : string = "a"
    if(activeLink != label){
      return classDisable
    }else return classDefault
  }

  const link = ({ label }: { label: string }) : ReactElement => {
    return (
      <li onClick={() => getLink(label)} className="breadcrumb-item">
        <a href="#" className={editClassLink(label)} tabIndex={-1} role="button" aria-disabled="true">{label}</a>
      </li>
    )
  }

  const getLink = (label: String) => {
    Streamlit.setComponentValue(label)
    activeLink = label
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
