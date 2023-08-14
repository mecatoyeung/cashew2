import styles from '../../styles/Editor.module.css'

const StreamSeparator = (props) => {

  return (
    <div className={styles.separator}>
      <i className="bi bi-arrow-down"></i>
      <i className="bi bi-arrow-down"></i>
      <i className="bi bi-arrow-down"></i>
    </div>
  )
}

export default StreamSeparator