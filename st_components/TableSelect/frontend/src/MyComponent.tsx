import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useCallback, useEffect, useMemo, useState, ReactElement } from "react"

function MyComponent({ args, disabled, theme }: ComponentProps): ReactElement {
  const [isHovered, setIsHovered] = useState(false)

  const style: React.CSSProperties = useMemo(() => {
    if (!theme) return {}

    const backgroundColor = `backgroundColor: ${isHovered ? (theme as any).primaryColor : "transparent"}`
    const borderColor = `${(theme as any).borderColor}`
    return { borderColor }
  }, [theme])

  useEffect(() => {
    //
  }, [])

  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [])

  const onMouseOver = useCallback((): void => {
    setIsHovered(true)
    localStorage.setItem("key", "value")
  }, [])

  const onMouseOut = useCallback((): void => {
    setIsHovered(false)
    console.log("table --> ", localStorage.setItem("key", "value"))
  }, [])

  return (
    <span>
      <div className="TableSelect_Header flex">
        <div className="TableSelect_Col_1">Experiment name</div>
        <div className="flex-1"></div>
        <div className="TableSelect_Col_2">Type</div>
      </div>
      <div className="TableSelect_Body">
        <div style={style} onMouseOver={onMouseOver} onMouseOut={onMouseOut} className="TableSelect_Row flex">
          <div className="TableSelect_Col_1">Immunoprecipitation</div>
          <div className="flex-1"></div>
          <div className="TableSelect_Col_2">PI</div>
        </div>
        <div style={style} className="TableSelect_Row flex">
          <div className="TableSelect_Col_1">MS screen</div>
          <div className="flex-1"></div>
          <div className="TableSelect_Col_2">non-PI</div>
        </div>
      </div>
    </span>
  )
}

export default withStreamlitConnection(MyComponent)
