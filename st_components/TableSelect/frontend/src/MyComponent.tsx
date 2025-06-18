import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useCallback, useEffect, useMemo, useState, ReactElement } from "react"

type BUTTON_2_COLUMNS = {
  absolute_index: number,
  text: string,
  type: string,
  background_color:string,
  text_color:string
}

type BUTTON_1_COLUMNS = {
  absolute_index: number,
  text: string,
  background_color:string,
  text_color:string
}

function MyComponent({ args, disabled, theme }: ComponentProps): ReactElement {
  const {header, buttons, columns} = args
//  console.log(buttons)
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

  const style_solution = (background_color: string,text_color:string): React.CSSProperties => {
    let backgroundColor = `${background_color}`
    let color = `${text_color}`

    return {
      color,
      backgroundColor
    }
  }

  useEffect(() => {
    Streamlit.setFrameHeight()
    Streamlit.setComponentValue(buttons[isActive])
  }, [])

  const setActive = useCallback((button) => {
    setIsActive(button)
//    console.log(button)
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

  const button_two_collumns = ({ absolute_index,text,type,background_color,text_color }: BUTTON_2_COLUMNS) : ReactElement => {
    return (
      <div key={text} style={style(absolute_index,background_color,text_color)} onClick={() => setActive(absolute_index)} className={`TableSelect_Row ${isRowActive(absolute_index) ? 'active' : ''}`}>
        <div className="flex">
          <div className="TableSelect_Col_1">{text}</div>
          <div className="flex-1"></div>
          <div className="TableSelect_Col_2">{type}</div>
        </div>
        <div className="solutions">
          <div style={style_solution(background_color,text_color)} className="solution">sfsdfsfsdf</div>
          <div style={style_solution(background_color,text_color)} className="solution">sfsdfsfsdf</div>
        </div>
      </div>
    )
  }

  const button_one_collumn = ({ absolute_index,text,background_color,text_color }: BUTTON_1_COLUMNS) : ReactElement => {
    return (
      <div key={text} style={style(absolute_index,background_color,text_color)} onClick={() => setActive(text)} className={`TableSelect_Row flex ${isRowActive(text) ? 'active' : ''}`}>
        <div className="TableSelect_Col_1">{text}</div>
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
        {columns === 2 ? buttons.filter((button:any) => button.text && button.type).map(button_two_collumns) : buttons.filter((button:any) => button.text).map(button_one_collumn)}
      </div>
    </span>
  )
}

export default withStreamlitConnection(MyComponent)
