import styles from '../../styles/Editor.module.css'

import Button from 'react-bootstrap/Button'
import Form from 'react-bootstrap/Form'
import Modal from 'react-bootstrap/Modal'
import Table from 'react-bootstrap/Table'

import Select from 'react-select'
import { useState } from 'react'



const conditionOptions = [
    {
      label: "equals",
      value: "equals"
    },
    {
        label: "regex",
        value: "regex"
    },
    {
        label: "contains",
        value: "contains"
    },
    {
      label: "is empty",
      value: "isEmpty"
    },
    {
      label: "is not empty",
      value: "isNotEmpty"
    }
  ]

const StreamConditions = (props) => {

    const [conditions, setConditions] = useState([])

    const txtConditionColumnChangeHandler = (index, value)=> {
        let updatedConditions = JSON.parse(props.conditions)
        updatedConditions[index].column = value
        let updatedConditionsInJSON = JSON.stringify(updatedConditions)
        setConditions(updatedConditionsInJSON)
        updateConditions(updatedConditionsInJSON)
    }

    const selectOperatorChangeHandler = (index, operator)=> {
        let updatedConditions = JSON.parse(props.conditions)
        updatedConditions[index].operator = operator.value
        let updatedConditionsInJSON = JSON.stringify(updatedConditions)
        setConditions(updatedConditionsInJSON)
        updateConditions(updatedConditionsInJSON)
    }

    const txtConditionValueChangeHandler = (index, value) => {
        let updatedConditions = JSON.parse(props.conditions)
        updatedConditions[index].value = value
        let updatedConditionsInJSON = JSON.stringify(updatedConditions)
        setConditions(updatedConditionsInJSON)
        updateConditions(updatedConditionsInJSON)
    }

    const addConditionButtonClickHandler = () => {
        let updatedConditions = JSON.parse(props.conditions)
        updatedConditions.push({
        column: "",
        condition: "equals",
        value: ""
        })
        let updatedConditionsInJSON = JSON.stringify(updatedConditions)
        setConditions(updatedConditionsInJSON)
        updateConditions(updatedConditionsInJSON)
    }

    const removeConditionButtonClickHandler = (conditionIndex) => {
        let updatedConditions = JSON.parse(props.conditions)
        updatedConditions = updatedConditions.filter((c, index) => index != conditionIndex)
        let updatedConditionsInJSON = JSON.stringify(updatedConditions)
        setConditions(updatedConditionsInJSON)
        updateConditions(updatedConditionsInJSON)
    }

  const updateConditions = (conditions) => {
    props.onUpdateConditions(conditions)
  }

  return (
    <>
    {JSON.parse(props.conditions).length > 0 && (
        <Table striped bordered hover>
            <thead>
            <tr>
                <th>#</th>
                <th>Column</th>
                <th>Operator</th>
                <th>Value</th>
                <th></th>
            </tr>
            </thead>
            <tbody>
            {JSON.parse(props.conditions).map((condition, conditionIndex) => (
                <tr key={conditionIndex}>
                <td>{conditionIndex + 1}</td>
                <td>
                    <Form.Control value={condition.column} onChange={(e) => txtConditionColumnChangeHandler(conditionIndex, e.target.value)}/>
                </td>
                <td>
                    <Select
                    options={conditionOptions}
                    value={conditionOptions.find(o => o.value == condition.operator)}
                    onChange={(e) => selectOperatorChangeHandler(conditionIndex, e)}
                    menuPlacement="auto"
                    menuPosition="fixed" />
                </td>
                <td>
                    <Form.Control value={condition.value} onChange={(e) => txtConditionValueChangeHandler(conditionIndex, e.target.value)}/>
                </td>
                <td>
                    <Button variant="danger" onClick={() => removeConditionButtonClickHandler(conditionIndex)}>
                    Remove
                    </Button>
                </td>
                </tr>
            ))}
            </tbody>
        </Table>
    )}
    <Button variant='primary' onClick={addConditionButtonClickHandler}>
        Add Condition
    </Button>
    </>
  )
}

export default StreamConditions