import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Image from 'next/image'
import Head from 'next/head'

import { produce } from "immer"

import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Form from 'react-bootstrap/Form'
import { Button } from 'react-bootstrap'

import Select from 'react-select'

import service from '../../service'

import OnePageLayout from '../../layouts/onePage'

import signUpStyles from "../../styles/SignUp.module.css"

import Loader from '../../assets/icons/loader.svg'

export default function SignUp() {

  const router = useRouter()

  const [formValidation, setFormValidation] = useState({
    isValid: true,
    errorMessages: {
      username: "",
      email: "",
      password1: "",
      password2: "",
      fullName: "",
      country: "",
      companyName: ""
    }
  })

  const [formSuccessMessage, setFormSuccessMessage] = useState("")
  const [formErrorMessages, setFormErrorMessages] = useState(null)

  const [signUpForm, setSignUpForm] = useState({
    username: "",
    email: "",
    password1: "",
    password2: "",
    fullName: "",
    country: "",
    companyName: "",
    submitting: false
  })

  const [userCountries, setUserCountries] = useState([])

  const fullNameChangeHandler = (e) => {
    setSignUpForm(
      produce((draft) => {
        draft.fullName = e.target.value
      })
    )
  }

  const companyNameChangeHandler = (e) => {
    setSignUpForm(
      produce((draft) => {
        draft.companyName = e.target.value
      })
    )
  }

  const countryChangeHandler = (e) => {
    setSignUpForm(
      produce((draft) => {
        draft.country = e.value
      })
    )
  }

  const emailChangeHandler = (e) => {
    setSignUpForm(
      produce((draft) => {
        draft.username = e.target.value
        draft.email = e.target.value
      })
    )
  }

  const passwordChangeHandler = (e) => {
    setSignUpForm(
      produce((draft) => {
        draft.password1 = e.target.value
      })
    )
  }

  const confirmPasswordChangeHandler = (e) => {
    setSignUpForm(
      produce((draft) => {
        draft.password2 = e.target.value
      })
    )
  }

  const signUpBtnClickHandler = (e) => {
    e.preventDefault()
    if (validateSignUpForm()) {
      let updatedSignUpForm = {...signUpForm}
      updatedSignUpForm.submitting = true
      setSignUpForm(updatedSignUpForm)
      setFormErrorMessages(null)

      localStorage.removeItem("token")

      service.post("rest-auth/registration/",
        signUpForm,
        response => {
          if (response.status == 201) {
            updatedSignUpForm.submitting = false
            setSignUpForm(updatedSignUpForm)
            router.push("/verify-email?email=" + signUpForm.email)
            setFormSuccessMessage("Your account has been created. Please sign in.")
          }
        },
        error => {
          updatedSignUpForm.submitting = false
          setSignUpForm(updatedSignUpForm)
          setFormErrorMessages(error.response.data)
        }
      )
    }

  }

  const validateSignUpForm = () => {
    let isValid = true
    let errorMessages = []

    let emailRegex = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/

    if (signUpForm.fullName.length <= 0) {
      errorMessages.fullName = "'Full Name' cannot be empty."
      isValid = false
    }
    if (signUpForm.email.length <= 0) {
      errorMessages.email = "'Email' cannot be empty."
      isValid = false
    } else if (!emailRegex.test(signUpForm.email)) {
      errorMessages.email = "'Email' format is not correct."
      isValid = false
    }
    if (signUpForm.password1.length <= 0) {
      errorMessages.password1 = "'Password' cannot be empty."
      isValid = false
    }
    if (signUpForm.password2.length <= 0) {
      errorMessages.password2 = "'Confirm Password' cannot be empty."
      isValid = false
    }
    if (signUpForm.password1 != signUpForm.password2) {
      errorMessages.password2 = "'Confirm Password' is not matched with 'Password'."
      isValid = false
    }
    setFormValidation({
      isValid,
      errorMessages
    })
    return isValid
  }

  const getUserCountries = () => {
    service.get("/user_countries/", response => {
      setUserCountries(response.data)
    })
  }

  useEffect(() => {
    getUserCountries()
  }, [])

  return (
    <>
      <Head>
        <title>Cashew - Sign Up</title>
      </Head>
      <OnePageLayout>
        <div className={signUpStyles.wrapper}>
          <div>
            <i className={signUpStyles.backBtn + " bi" + " bi-arrow-left"} onClick={(() => router.back())}></i>
            <h1 className={signUpStyles.h1}>Sign up now!</h1>
          </div>
          <div className={signUpStyles.form}>
            <Form>
              <Row>
                <Form.Group as={Col} className={signUpStyles.col + " xs-12" + " md-3"} controlId="formFullName">
                  <Form.Label>Full Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="fullName"
                    placeholder="Enter full name"
                    onChange={(e) => fullNameChangeHandler(e)}
                    value={signUpForm.fullName}/>
                    {!formValidation.isValid && (
                      <div className="formErrorMessage">
                        {formValidation.errorMessages.fullName}
                      </div>
                    )}
                </Form.Group>
              </Row>
              <Row>
                <Form.Group as={Col} className={signUpStyles.col + " xs-12" + " md-3"} controlId="formCountry">
                  <Form.Label>Country</Form.Label>
                  <Select instanceId="userCountriesSelectId" options={userCountries} onChange={countryChangeHandler}/>
                </Form.Group>
              </Row>
              <Row>
                <Form.Group as={Col} className={signUpStyles.col + " xs-12" + " md-3"} controlId="formCompanyName">
                  <Form.Label>Company Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="companyName"
                    placeholder="Enter full name"
                    onChange={(e) => companyNameChangeHandler(e)}
                    value={signUpForm.companyName}/>
                    {!formValidation.isValid && (
                      <div className="formErrorMessage">
                        {formValidation.errorMessages.companyName}
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
                    autoComplete="username email"
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
                    autoComplete="new-password"
                    onChange={(e) => passwordChangeHandler(e)}
                    value={signUpForm.password1} />
                  {!formValidation.isValid && (
                      <div className="formErrorMessage">
                        {formValidation.errorMessages.password1}
                      </div>
                    )}
                </Form.Group>
              </Row>
              <Row className="xs-12 md-3">
                <Form.Group as={Col} className={signUpStyles.col + " xs-12" + " md-3"} controlId="formConfirmPassword">
                  <Form.Label>Confirm Password</Form.Label>
                  <Form.Control
                    type="password"
                    name="password2"
                    placeholder="Enter confirm password"
                    autoComplete="new-password"
                    onChange={(e) => confirmPasswordChangeHandler(e)}
                    value={signUpForm.password2} />
                    {!formValidation.isValid && (
                      <div className="formErrorMessage">
                        {formValidation.errorMessages.password2}
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
              <Row>
              {formErrorMessages && Object.keys(formErrorMessages).length > 0 && Object.keys(formErrorMessages).map(function(key, index) {
                return formErrorMessages[key].map(message => {
                  return (
                    <div className="formErrorMessage" key={message}>
                      {message}
                    </div>
                  )
                })
              })}
              </Row>
              <Row>
                <Form.Group as={Col} className={signUpStyles.actions + " " + signUpStyles.col + " xs-12" + " md-3"}>
                  <Button type="submit"
                          className={signUpStyles.signUpBtn + " " + signUpStyles.btn}
                          onClick={(e) => signUpBtnClickHandler(e)}
                          disabled={signUpForm.submitting}>
                            {signUpForm.submitting && <img className="spinner" src={Loader.src} />}{signUpForm.submitting ? "Loading": "Sign up"}</Button>
                  <Button type="button"
                          className={signUpStyles.signInBtn + " " + signUpStyles.btn + " btn-secondary"}
                          onClick={() => router.push("signin")}
                          disabled={signUpForm.submitting}>Sign in</Button>
                </Form.Group>
              </Row>
            </Form>
          </div>
        </div>
      </OnePageLayout>
    </>
  )
}
