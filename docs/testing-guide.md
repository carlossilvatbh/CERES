# Testing Guide

This guide explains how to run the automated tests for the CERES project.

## 📖 Table of Contents

- [Backend Tests](#backend-tests)
- [Frontend Tests](#frontend-tests)

## Backend Tests

Backend tests are written using Django's built‑in test framework.
Run them from the `backend` directory:

```bash
cd backend
python manage.py test
```

## Frontend Tests

The frontend project provides an npm script for running tests. Execute it inside
 the `frontend` directory:

```bash
cd frontend
npm test
```
