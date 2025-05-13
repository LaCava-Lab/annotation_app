import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useCallback, useEffect, useMemo, useState, ReactElement } from "react"

function MyComponent({ args, disabled, theme }: ComponentProps): ReactElement {
  const [isHovered, setIsHovered] = useState(false)
  const [isActive, setIsActive] = useState("")

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

  const setActive = useCallback((category) => {
    setIsActive(category)
    Streamlit.setComponentValue(category)

    if (isActive === category) {
      setIsActive("")
      Streamlit.setComponentValue("")
    }
}, [isActive])

  const isRowActive = useCallback((category): Boolean => {
    return isActive === category;
  }, [isActive])

  return (
    <span className="disable-select">
      <div className="TableSelect_Header flex">
        <div className="TableSelect_Col_1">Experiment name</div>
        <div className="flex-1"></div>
        <div className="TableSelect_Col_2">Type</div>
      </div>
      <div className="TableSelect_Body">
        <div style={style} onClick={() => setActive("Immunoprecipitation")} onMouseOver={onMouseOver} onMouseOut={onMouseOut} className={`TableSelect_Row flex ${isRowActive('Immunoprecipitation') ? 'active' : ''}`}>
          <div className="TableSelect_Col_1">Immunoprecipitation</div>
          <div className="flex-1"></div>
          <div className="TableSelect_Col_2">PI</div>
        </div>
        <div style={style} onClick={() => setActive("MS screen")} className={`TableSelect_Row flex ${isRowActive('MS screen') ? 'active' : ''}`}>
          <div className="TableSelect_Col_1">MS screen</div>
          <div className="flex-1"></div>
          <div className="TableSelect_Col_2">non-PI</div>
        </div>
      </div>
    </span>
  )
}

export default withStreamlitConnection(MyComponent)
