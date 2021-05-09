!compile w/ shared library: 'gfortran -o run_test -L ./pythonANN/ -lplugin test_pythonANN.f90'

PROGRAM COUPLING_TEST
   use, intrinsic :: iso_c_binding
   implicit none
   INTEGER, PARAMETER :: dp = SELECTED_REAL_KIND(P=15)
   interface
      subroutine get_rates(x1, x2, x3, x4, x5, n, y1, y2, b, dir, charlen) bind (c)
         use iso_c_binding
         INTEGER, PARAMETER :: dp = SELECTED_REAL_KIND(P=15)
         REAL (KIND=dp)                         :: x1
         REAL (KIND=dp)                         :: x2
         REAL (KIND=dp)                         :: x3
         integer(c_int)                         :: n
         REAL (KIND=dp)                         :: x4(n)
         REAL (KIND=dp)                         :: x5(n)
         REAL (KIND=dp)                         :: y1
         REAL (KIND=dp)                         :: y2
         integer(c_int)                         :: b
         integer(c_int)                         :: charlen
         character(kind=c_char)                 :: dir(charlen)
      end subroutine get_rates
   end interface

   !DECLARE INPUT PARAMETERS
   REAL (KIND=dp)                               :: T_gas
   REAL (KIND=dp)                               :: nH
   REAL (KIND=dp)                               :: n_H

   REAL (KIND=dp), allocatable                  :: l(:)
   integer                                      :: l_count
   REAL (KIND=dp), allocatable                  :: u(:)
   integer                                      :: u_count

   !DECLARE OUPUTS
   REAL (KIND=dp)                               :: LH
   REAL (KIND=dp)                               :: ER

   !LOOPING AND TIMING
   integer                                      :: i
   integer                                      :: ANNcount = 0
   REAL (KIND=dp)                               :: time1
   REAL (KIND=dp)                               :: time2

   !writing checkpoints
   INTEGER                             :: b_checkpoints             ! boolean int: do we save ANN checkpoints (0 or 1)
   INTEGER, PARAMETER                  :: modelelen = 100           ! length of simname char
   CHARACTER(LEN=modelelen)            :: modele    = 'simX'        ! Root name of output files



   !ASSIGN INPUT VALUES (sample 1 of testT01)
   T_gas = 4.113083490000000353e+01_dp
   nH = 1.194153369999999995e+05_dp
   n_H = 1.000000000000000000e+08_dp

   !read in lambda from test file
	open (unit=1, file='./test_data/lam_test.txt', status='old', action='read')

		read(1,*) l_count
		allocate (l(l_count))

        read(1,*) l

	close(1)

   !read in u from test file
   	open (unit=1, file='./test_data/u_test.txt', status='old', action='read')

		read(1,*) u_count
		allocate (u(u_count))

        read(1,*) u

	close(1)


   !!!! ACTION !!!!
   b_checkpoints = 1
   DO i=1,100
       CALL CPU_TIME(time1)
       call get_rates(T_gas, nH, n_H, l, u, size(u), LH, ER, b_checkpoints, modele, modelelen)
       CALL CPU_TIME(time2)
       ANNcount = ANNcount+1
       WRITE(*,'(A11,ES10.3,A6,I4)') 'ANN call : ', time2 - time1, 's - no', ANNcount
       PRINT *, LH
       PRINT *, ER
   END DO


   !DESIRED OUTPUT: (LABEL)
   ! LH 4.454582101342124460e-18
   ! ER 1.761998920326483102e-19

   !EXPECTED OUTPUT: (pyANN)
   ! LH 4.4375609429122016e-18
   ! ER 1.7884691743859221e-19

END PROGRAM COUPLING_TEST



