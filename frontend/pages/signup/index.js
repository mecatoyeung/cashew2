import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Image from 'next/image'

import { produce } from "immer"

import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Form from 'react-bootstrap/Form'
import { Button } from 'react-bootstrap'

import service from '../../service'

import OnePageLayout from '../../layouts/onePage'

import signUpStyles from "../../styles/SignUp.module.scss"

export default function SignUp() {

  const router = useRouter()

  const [formValidation, setFormValidation] = useState({
    isValid: true,
    errorMessages: {
      displayName: "",
      email: "",
      password: "",
      confirmPassword: ""
    }
  })

  const [formSuccessMessage, setFormSuccessMessage] = useState("")
  const [formErrorSummaryMessage, setFormErrorSummaryMessage] = useState("")

  const [signUpForm, setSignUpForm] = useState({
    displayName: "",
    email: "",
    password: "",
    confirmPassword: ""
  })

  const displayNameChangeHandler = (e) => {
    setSignUpForm(
      produce((draft) => {
        draft.displayName = e.target.value
      })
    )
  }

  const emailChangeHandler = (e) => {
    setSignUpForm(
      produce((draft) => {
        draft.email = e.target.value
      })
    )
  }

  const passwordChangeHandler = (e) => {
    setSignUpForm(
      produce((draft) => {
        draft.password = e.target.value
      })
    )
  }

  const confirmPasswordChangeHandler = (e) => {
    setSignUpForm(
      produce((draft) => {
        draft.confirmPassword = e.target.value
      })
    )
  }

  const signUpBtnClickHandler = (e) => {
    e.preventDefault()
    if (validateSignUpForm()) {
      service.post("api/account/create/",
        signUpForm,
        response => {
          if (response.status == 201) {
            // if response is valid and account is created
            setFormSuccessMessage("Your account has been created. Please sign in.")
          }
        },
        error => {
          setFormErrorSummaryMessage(error.response.data.errorMessage)
        }
      )
    }

  }

  const validateSignUpForm = () => {
    let isValid = true
    let errorMessages = []

    let emailRegex = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/

    if (signUpForm.displayName.length <= 0) {
      errorMessages.displayName = "'Display Name' cannot be empty."
      isValid = false
    }
    if (signUpForm.email.length <= 0) {
      errorMessages.email = "'Email' cannot be empty."
      isValid = false
    } else if (!emailRegex.test(signUpForm.email)) {
      errorMessages.email = "'Email' format is not correct."
      isValid = false
    }
    if (signUpForm.password.length <= 0) {
      errorMessages.password = "'Password' cannot be empty."
      isValid = false
    }
    if (signUpForm.confirmPassword.length <= 0) {
      errorMessages.confirmPassword = "'Confirm Password' cannot be empty."
      isValid = false
    }
    if (signUpForm.password != signUpForm.confirmPassword) {
      errorMessages.confirmPassword = "'Confirm Password' is not matched 'Password'."
      isValid = false
    }
    setFormValidation({
      isValid,
      errorMessages
    })
    return isValid
  }

  return (
    <OnePageLayout>
      <div className={signUpStyles.wrapper}>
        <div>
          <i className={signUpStyles.backBtn + " bi" + " bi-arrow-left"} onClick={(() => router.back())}></i>
          <h1 className={signUpStyles.h1}>Sign up now!</h1>
        </div>
        <div className={signUpStyles.form}>
          <Form>
            <Row>
              <Form.Group as={Col} className={signUpStyles.col + " xs-12" + " md-3"} controlId="formDisplayName">
                <Form.Label>Display Name</Form.Label>
                <Form.Control
                  type="text"
                  name="displayName"
                  placeholder="Enter display name"
                  onChange={(e) => displayNameChangeHandler(e)}
                  value={signUpForm.displayName}/>
                  {!formValidation.isValid && (
                    <div className="formErrorMessage">
                      {formValidation.errorMessages.displayName}
                    </div>
                  )}
              </Form.Group>
            </Row>
            <Row>
              <Form.Group as={Col} className={signUpStyles.col + " xs-12" + " md-3"} controlId="formEmail">
                <Form.Label>Email</Form.Label>
                <Form.Control
                  type="email"
                  name="email"
                  placeholder="Enter email"
                  onChange={(e) => emailChangeHandler(e)}
                  value={signUpForm.email} />
                {!formValidation.isValid && (
                    <div className="formErrorMessage">
                      {formValidation.errorMessages.email}
                    </div>
                  )}
              </Form.Group>
            </Row>
            <Row className="xs-12 md-3">
              <Form.Group as={Col} className={signUpStyles.col + " xs-12" + " md-3"} controlId="formPassword">
                <Form.Label>Password</Form.Label>
                <Form.Control
                  type="password"
                  name="password"
                  placeholder="Enter password"
                  onChange={(e) => passwordChangeHandler(e)}
                  value={signUpForm.password} />
                {!formValidation.isValid && (
                    <div className="formErrorMessage">
                      {formValidation.errorMessages.password}
                    </div>
                  )}
              </Form.Group>
            </Row>
            <Row className="xs-12 md-3">
              <Form.Group as={Col} className={signUpStyles.col + " xs-12" + " md-3"} controlId="formConfirmPassword">
                <Form.Label>Confirm Password</Form.Label>
                <Form.Control
                  type="password"
                  name="confirmPassword"
                  placeholder="Enter confirm password"
                  onChange={(e) => confirmPasswordChangeHandler(e)}
                  value={signUpForm.confirmPassword} />
                {!formValidation.isValid && (
                    <div className="formErrorMessage">
                      {formValidation.errorMessages.confirmPassword}
                    </div>
                  )}
              </Form.Group>
            </Row>
            {formSuccessMessage && formSuccessMessage.length > 0 && (
              <Row>
                <div className="formSuccessMessage">
                  {formSuccessMessage}
                </div>
              </Row>
            )}
            {formErrorSummaryMessage && formErrorSummaryMessage.length > 0 && (
              <Row>
                <div className="formErrorSummaryMessage">
                  {formErrorSummaryMessage}
                </div>
            </Row>
            )}
            <Row>
              <Form.Group as={Col} className={signUpStyles.actions + " " + signUpStyles.col + " xs-12" + " md-3"}>
                <Button type="submit" className={signUpStyles.signUpBtn + " " + signUpStyles.btn} onClick={(e) => signUpBtnClickHandler(e)}>Sign up</Button>
                <Button type="button" className={signUpStyles.signInBtn + " " + signUpStyles.btn + " btn-secondary"} onClick={() => router.push("signin")}>Sign in</Button>
              </Form.Group>
            </Row>
          </Form>
        </div>
      </div>
    </OnePageLayout>
  )
}
