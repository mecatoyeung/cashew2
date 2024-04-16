import dynamic from 'next/dynamic'

const CodeEditor = dynamic(
  () => import('@uiw/react-textarea-code-editor').then((mod) => mod.default),
  { ssr: false }
)

import '@uiw/react-textarea-code-editor/dist.css'

import styles from '../../styles/Editor.module.css'

const StreamTable = (props) => {
  return (
    <>
      {props.stream.data.type == 'TEXTFIELD' && (
        <div className={styles.streamTableDiv}>
          <table className={styles.streamTable}>
            <tbody>
              {props.stream.data.value.map((row, rowIndex) => {
                return (
                  <tr key={rowIndex}>
                    <td>{row.toString().replace(/ /g, '\u00a0')}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
      {props.stream.data.type == 'ANCHORED_TEXTFIELD' && (
        <div className={styles.streamTableDiv}>
          <table className={styles.streamTable}>
            <tbody>
              {props.stream.data.value.map((row, rowIndex) => {
                return (
                  <tr key={rowIndex}>
                    <td>{row.replace(/ /g, '\u00a0')}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
      {props.stream.data.type == 'BARCODE' && (
        <div className={styles.streamTableDiv}>
          <table className={styles.streamTable}>
            <tbody>
              {props.stream.data.value.map((row, rowIndex) => {
                return (
                  <tr key={rowIndex}>
                    <td>{row.replace(/ /g, '\u00a0')}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
      {props.stream.data.type == 'ACROBAT_FORM' && (
        <div className={styles.streamTableDiv}>
          <table className={styles.streamTable}>
            <tbody>
              {props.stream.data.value.map((row, rowIndex) => {
                return (
                  <tr key={rowIndex}>
                    <td>{row.replace(/ /g, '\u00a0')}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
      {props.stream.data.type == 'TABLE' && (
        <div className={styles.streamTableDiv}>
          <table className={styles.streamTable}>
            <tbody>
              {props.stream.data.value.body.map((row, rowIndex) => {
                return (
                  <tr key={rowIndex}>
                    {row.map((col, colIndex) => {
                      return (
                        <td key={colIndex}>{col.replace(/ /g, '\u00a0')}</td>
                      )
                    })}
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
      {props.stream.data.type == 'JSON' && (
        <div className={styles.streamTableDiv}>
          <table className={styles.streamTable}>
            <tbody>
              <CodeEditor
                id={'json-editor'}
                value={props.stream.data.value}
                language="js"
                padding={15}
                style={{
                  border: '1px solid #333',
                }}
              />
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}

export default StreamTable
