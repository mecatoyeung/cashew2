import styles from '../../styles/Editor.module.css'

const StreamTable = (props) => {

  return (
    <>
      {props.stream.type == "TEXTFIELD" && (
        <div className={styles.streamTableDiv}>
          <table className={styles.streamTable}>
            <tbody>
              {props.stream.data.map((row, rowIndex) => {
                return (
                  <tr key={rowIndex}>
                    <td>{row.replace(/ /g, "\u00a0")}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
      {props.stream.type == "ANCHORED_TEXTFIELD" && (
        <div className={styles.streamTableDiv}>
          <table className={styles.streamTable}>
            <tbody>
              {props.stream.data.map((row, rowIndex) => {
                return (
                  <tr key={rowIndex}>
                    <td>{row.replace(/ /g, "\u00a0")}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
      {props.stream.type == "BARCODE" && (
        <div className={styles.streamTableDiv}>
          <table className={styles.streamTable}>
            <tbody>
              {props.stream.data.map((row, rowIndex) => {
                return (
                  <tr key={rowIndex}>
                    <td>{row.replace(/ /g, "\u00a0")}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
      {props.stream.type == "ACROBAT_FORM" && (
        <div className={styles.streamTableDiv}>
          <table className={styles.streamTable}>
            <tbody>
              {props.stream.data.map((row, rowIndex) => {
                return (
                  <tr key={rowIndex}>
                    <td>{row.replace(/ /g, "\u00a0")}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
      {props.stream.type == "TABLE" && (
        <div className={styles.streamTableDiv}>
          <table className={styles.streamTable}>
            <tbody>
              {props.stream.data.body.map((row, rowIndex) => {
                return (
                  <tr key={rowIndex}>
                    {row.map((col, colIndex) => {
                      return (
                        <td key={colIndex}>{col.replace(/ /g, "\u00a0")}</td>
                      )
                    })}
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}

export default StreamTable