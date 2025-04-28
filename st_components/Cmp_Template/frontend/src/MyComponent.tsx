import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useCallback, useEffect, useMemo, useState, ReactElement } from "react"

function MyComponent({args, disabled, theme}: ComponentProps): ReactElement {

  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [])

//    <!-- create your own html -->
  return (
    <span>
    </span>
  )
}

export default withStreamlitConnection(MyComponent)
