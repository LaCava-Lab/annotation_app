import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useCallback, useEffect, useMemo, useState, ReactElement } from "react"

type BUTTON_2_COLUMNS = {
  index: number,
  name: string,
  type: string,
  background_color:string,
  text_color:string
}

type BUTTON_1_COLUMNS = {
  index: number,
  name: string,
  background_color:string,
  text_color:string
}

function MyComponent({ args, disabled, theme }: ComponentProps): ReactElement {
  const {header, buttons, columns} = args
  console.log(buttons)
  const [isActive, setIsActive] = useState(0)


  const style = (index: number, background_color: string,text_color:string): React.CSSProperties => {
    let backgroundColor = ""
    let color = ""
    if (isActive === index) {
      backgroundColor = `${background_color}`
      color = `${text_color}`
    }
    return {
      color,
      backgroundColor,
      borderColor: `${(theme as any).borderColor}`,
      borderWidth: '1px',
      borderStyle: 'solid',
      cursor: 'pointer',
    }
  }

  useEffect(() => {
    Streamlit.setFrameHeight()
    Streamlit.setComponentValue(buttons[isActive])
  }, [])

  const setActive = useCallback((button) => {
    setIsActive(button)
    Streamlit.setComponentValue(buttons[button])
//    Streamlit.setComponentValue(buttons[button])
//    if (isActive > 0)

//    if (isActive === button) {
//      setIsActive(-1)
//      Streamlit.setComponentValue([])
//    }
}, [buttons])

  const isRowActive = useCallback((category): Boolean => {
    return isActive === category;
  }, [isActive])

  const button_two_collumns = ({ index,name,type,background_color,text_color }: BUTTON_2_COLUMNS) : ReactElement => {
    return (
      <div key={name} style={style(index,background_color,text_color)} onClick={() => setActive(index)} className={`TableSelect_Row flex ${isRowActive(index) ? 'active' : ''}`}>
        <div className="TableSelect_Col_1">{name}</div>
        <div className="flex-1"></div>
        <div className="TableSelect_Col_2">{type}</div>
      </div>
    )
  }

  const button_one_collumn = ({ index,name,background_color,text_color }: BUTTON_1_COLUMNS) : ReactElement => {
    return (
      <div key={name} style={style(index,background_color,text_color)} onClick={() => setActive(name)} className={`TableSelect_Row flex ${isRowActive(name) ? 'active' : ''}`}>
        <div className="TableSelect_Col_1">{name}</div>
      </div>
    )
  }

  return (
    <span className="disable-select">
      <div className="TableSelect_Header flex">
        <div className="TableSelect_Col_1">{header.column_1}</div>
        {columns === 2 ? (
          <>
            <div className="flex-1"></div>
            <div className="TableSelect_Col_2">{header.column_2}</div>
          </>
        ) : null}
      </div>
      <div className="TableSelect_Body">
        {columns === 2 ? buttons.filter((button:any) => button.name && button.type).map(button_two_collumns) : buttons.filter((button:any) => button.name).map(button_one_collumn)}
      </div>
    </span>
  )
}

export default withStreamlitConnection(MyComponent)
